use postflop_solver::*;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::collections::HashMap;
use std::fs;
use std::path::Path;
use std::path::PathBuf;

#[pyfunction]
fn solve_poker_spot(py: Python, inputs: &PyDict) -> PyResult<PyObject> {
    // Extract inputs from the Python dictionary
    let effective_stack: i32 = inputs.get_item("effective_stack").unwrap().extract()?;
    let pot_before_flop: i32 = inputs.get_item("pot_before_flop").unwrap().extract()?;
    let preflop_action: String = inputs.get_item("preflop_action").unwrap().extract()?;
    let flop_cards: String = inputs.get_item("flop_card").unwrap().extract()?;
    let flop_actions: Option<String> = inputs.get_item("flop_action").unwrap().extract()?;
    let turn_card: Option<String> = inputs.get_item("turn_card").unwrap().extract()?;
    let turn_actions: Option<String> = inputs.get_item("turn_action").unwrap().extract()?;
    let river_card: Option<String> = inputs.get_item("river_card").unwrap().extract()?;
    let river_actions: Option<String> = inputs.get_item("river_action").unwrap().extract()?;
    let final_pot: f32 = inputs.get_item("final_pot").unwrap().extract()?;

    let (ranges_path, position1, position2) = construct_ranges_path(&preflop_action);
    println!("Ranges path: {}", ranges_path);

    // Determine who is in position
    let order1 = position_to_order(&position1);
    let order2 = position_to_order(&position2);

    let (oop_position, ip_position) = if order1 < order2 {
        (position1.clone(), position2.clone())
    } else {
        (position2.clone(), position1.clone())
    };
    // println!("OOP: {}, IP: {}", oop_position, ip_position);

    // Now read the ranges for OOP and IP
    let oop_range_file = format!("{}/{}.txt", ranges_path, oop_position);
    let ip_range_file = format!("{}/{}.txt", ranges_path, ip_position);

    // println!("OOP range file: {}", oop_range_file);
    // println!("IP range file: {}", ip_range_file);

    // Read the ranges from the file
    let oop_range_str = fs::read_to_string(oop_range_file).map_err(|_| {
        PyErr::new::<pyo3::exceptions::PyIOError, _>("Failed to read OOP range file")
    })?;
    let ip_range_str = fs::read_to_string(ip_range_file).map_err(|_| {
        PyErr::new::<pyo3::exceptions::PyIOError, _>("Failed to read IP range file")
    })?;

    // Create ranges
    let oop_range = oop_range_str.parse::<Range>().unwrap();
    let ip_range = ip_range_str.parse::<Range>().unwrap();

    // Parse flop, turn, river cards
    let flop = flop_from_str(&flop_cards).unwrap();
    let turn = if let Some(card) = turn_card {
        card_from_str(&card).unwrap()
    } else {
        NOT_DEALT
    };
    let river = if let Some(card) = river_card {
        card_from_str(&card).unwrap()
    } else {
        NOT_DEALT
    };

    // Set up card configuration
    let card_config = CardConfig {
        range: [oop_range, ip_range],
        flop: flop,
        turn: NOT_DEALT,
        river: NOT_DEALT,
    };

    // Define bet sizes (simplified for this example)
    let bet_sizes = BetSizeOptions::try_from(("33%, 75%, 150%, a", "33%, 100%, a")).unwrap();
    let donk_sizes = DonkSizeOptions::try_from(("33%")).unwrap();
    // Set up tree configuration
    let tree_config = TreeConfig {
        initial_state: BoardState::Flop,
        starting_pot: pot_before_flop,
        effective_stack,
        rake_rate: 0.0,
        rake_cap: 0.0,
        flop_bet_sizes: [bet_sizes.clone(), bet_sizes.clone()],
        turn_bet_sizes: [bet_sizes.clone(), bet_sizes.clone()],
        river_bet_sizes: [bet_sizes.clone(), bet_sizes],
        turn_donk_sizes: Some(donk_sizes.clone()),
        river_donk_sizes: Some(donk_sizes),
        add_allin_threshold: 1.5,
        force_allin_threshold: 0.15,
        merging_threshold: 0.1,
    };

    // Build the game tree and create the game
    let action_tree = ActionTree::new(tree_config).unwrap();
    let mut game = PostFlopGame::with_config(card_config, action_tree).unwrap();

    // Allocate memory and solve the game
    game.allocate_memory(false);
    let max_num_iterations = 1000;
    let target_exploitability = game.tree_config().starting_pot as f32 * 0.01;
    solve(&mut game, max_num_iterations, target_exploitability, true);

    // Cache normalized weights

    if let Some(flop_actions) = flop_actions {
        for num_str in flop_actions.split(',') {
            // Convert the string slice to an integer
            match num_str.trim().parse::<usize>() {
                Ok(num) => game.play(num),
                Err(_) => println!("Invalid number: {}", num_str),
            }
        }
    }

    if turn != NOT_DEALT {
        game.play(turn as usize);
        if let Some(turn_actions) = turn_actions {
            for num_str in turn_actions.split(',') {
                // Convert the string slice to an integer
                match num_str.trim().parse::<usize>() {
                    Ok(num) => game.play(num),
                    Err(_) => println!("Invalid number: {}", num_str),
                }
            }
        }
    }

    if river != NOT_DEALT {
        game.play(river as usize);
        if let Some(river_actions) = river_actions {
            for num_str in river_actions.split(',') {
                // Convert the string slice to an integer
                match num_str.trim().parse::<usize>() {
                    Ok(num) => game.play(num),
                    Err(_) => println!("Invalid number: {}", num_str),
                }
            }
        }
    }

    game.cache_normalized_weights();

    // Get equities and EVs for both players
    let equities_oop = game.equity(0);
    let evs_oop = game.expected_values(0);
    let equities_ip = game.equity(1);
    let evs_ip = game.expected_values(1);

    // Get the hand strings
    let oop_hands = game.private_cards(0);
    let ip_hands = game.private_cards(1);
    let oop_hands_str = holes_to_strings(&oop_hands).unwrap();
    let ip_hands_str = holes_to_strings(&ip_hands).unwrap();

    // Create dictionaries for hero and villain
    let mut hero_dict = PyDict::new(py);
    for (i, hand_str) in oop_hands_str.iter().enumerate() {
        let mut hand_info = PyDict::new(py);
        hand_info.set_item("EV", evs_oop[i])?;
        hand_info.set_item("Equity", equities_oop[i])?;
        // Handle division by zero
        let eqr = if equities_oop[i] != 0.0 && final_pot != 0.0 {
            (evs_oop[i] / equities_oop[i]) / final_pot
        } else {
            0.0
        };
        hand_info.set_item("EQR", eqr)?;
        hero_dict.set_item(hand_str, hand_info)?;
    }

    // Convert the legal actions to a list
    let action_list = game.available_actions();
    let mut action_list_ret = PyDict::new(py);
    for (i, action) in action_list.iter().enumerate() {
        action_list_ret.set_item(i, action.to_string())?;
    }
    // Calculate Hero overall range action probabilities
    let hero_range_action_prob = game.strategy();
    let num_hands = oop_hands_str.len();
    let num_actions = hero_range_action_prob.len() / num_hands;

    for (i, hand_str) in oop_hands_str.iter().enumerate() {
        let mut actions_prob_list = Vec::new();
        for j in 0..num_actions {
            let prob = hero_range_action_prob[j * num_hands + i];
            actions_prob_list.push(prob);
        }
        hero_dict
            .get_item(hand_str)
            .unwrap()
            .set_item("Actions Probabilities", actions_prob_list)?;
    }

    let mut villain_dict = PyDict::new(py);
    for (i, hand_str) in ip_hands_str.iter().enumerate() {
        let mut hand_info = PyDict::new(py);
        hand_info.set_item("EV", evs_ip[i])?;
        hand_info.set_item("Equity", equities_ip[i])?;
        let eqr = if equities_ip[i] != 0.0 && final_pot != 0.0 {
            (evs_ip[i] / equities_ip[i]) / final_pot
        } else {
            0.0
        };
        hand_info.set_item("EQR", eqr)?;
        villain_dict.set_item(hand_str, hand_info)?;
    }

    // Calculate equity buckets
    let hero_buckets = calculate_equity_buckets(&equities_oop);
    let villain_buckets = calculate_equity_buckets(&equities_ip);

    // Prepare the result dictionary
    let result = PyDict::new(py);
    result.set_item("Hero", hero_dict)?;
    result.set_item("Villain", villain_dict)?;
    result.set_item("Hero Equity Buckets", hero_buckets)?;
    result.set_item("Villain Equity Buckets", villain_buckets)?;
    result.set_item("Legal Actions", action_list_ret)?;

    Ok(result.into())
}

fn position_to_order(position: &str) -> u8 {
    match position {
        "SB" => 1,
        "BB" => 2,
        "UTG" => 3,
        "HJ" => 4,
        "CO" => 5,
        "BTN" => 6,
        _ => 0, // Unknown position
    }
}

fn construct_ranges_path(preflop_action: &str) -> (String, String, String) {
    // Base directory for ranges
    let mut path_elements = vec![
        "C:\\Users\\yixiu\\Desktop\\PokerGTOExplained\\backend\\postflop-solver\\GTOWizard_Scraped_Ranges\\Cash6m50z100bbGeneral"
            .to_string(),
    ];

    // Define the standard order of positions in a 6-max game
    let standard_positions = vec!["UTG", "HJ", "CO", "BTN", "SB", "BB"];

    // Split the action into positions
    let action_positions: Vec<&str> = preflop_action.split(",").collect();

    if action_positions.len() < 2 {
        panic!("Preflop action must have at least two positions");
    }

    // Keep track of positions that have raised
    let mut has_raised = HashMap::new();

    // Keep track of the action sequence
    let action_sequence = action_positions.clone();

    // Initialize last two positions
    let mut last_two_positions = Vec::new();

    // Process the action sequence
    let mut i = 0;
    while i < action_sequence.len() {
        let position = action_sequence[i];

        // Append the position to the path
        path_elements.push(position.to_string());

        // Get the action for this position
        let action = if i < action_sequence.len() - 1 {
            // Not the last action; get a non-call/all-in action
            if let Some(action) = get_non_call_allin_action(&PathBuf::from(path_elements.join("/")))
            {
                // Check if the action is a raise
                let is_raise = is_raise_action(&action);
                if is_raise {
                    has_raised.insert(position.to_string(), true);
                }
                action
            } else {
                panic!("No valid action found for position {}", position);
            }
        } else {
            // Last action; assume it's a call
            "call".to_string()
        };

        path_elements.push(action.clone());

        // Check for skipped positions that need to fold
        if i < action_sequence.len() - 1 {
            let next_position = action_sequence[i + 1];

            let skipped_positions =
                get_skipped_positions(&standard_positions, position, next_position);

            for skipped_position in skipped_positions {
                if has_raised.get(&skipped_position) == Some(&true) {
                    // Insert fold action for the skipped position
                    path_elements.push(skipped_position.to_string());
                    path_elements.push("fold".to_string());
                }
            }
        }

        // Collect the last two positions that took action
        if i >= action_sequence.len() - 2 {
            last_two_positions.push(position.to_string());
        }

        i += 1;
    }

    // Convert the path elements to a path string
    let path_str = path_elements.join("/");

    // Return the path and the last two positions
    (
        path_str,
        last_two_positions[0].clone(),
        last_two_positions[1].clone(),
    )
}

// Helper function to get skipped positions between two positions (with wrap-around)
fn get_skipped_positions(
    standard_positions: &[&str],
    current_position: &str,
    next_position: &str,
) -> Vec<String> {
    let num_positions = standard_positions.len();

    let current_index = standard_positions
        .iter()
        .position(|&p| p == current_position)
        .unwrap();
    let next_index = standard_positions
        .iter()
        .position(|&p| p == next_position)
        .unwrap();

    let mut skipped_positions = Vec::new();

    let mut index = (current_index + 1) % num_positions;

    while index != next_index {
        skipped_positions.push(standard_positions[index].to_string());
        index = (index + 1) % num_positions;
    }

    skipped_positions
}

// Helper function to determine if an action is a raise
fn is_raise_action(action: &str) -> bool {
    action != "call" && action != "allin" && action != "fold"
}

fn get_non_call_allin_action(position_path: &Path) -> Option<String> {
    if let Ok(entries) = fs::read_dir(position_path) {
        for entry in entries {
            if let Ok(entry) = entry {
                let file_name = entry.file_name();
                let action = file_name.to_string_lossy();
                if action != "call" && action != "allin" && entry.path().is_dir() {
                    return Some(action.to_string());
                }
            }
        }
    }
    None
}

fn calculate_equity_buckets(equities: &[f32]) -> [f32; 7] {
    let mut buckets = [0.0; 7];
    let total = equities.len() as f32;

    for &equity in equities {
        let percentage = equity * 100.0;
        let index = match percentage {
            x if x < 25.0 => 0,
            x if x < 50.0 => 1,
            x if x < 60.0 => 2,
            x if x < 70.0 => 3,
            x if x < 80.0 => 4,
            x if x < 90.0 => 5,
            _ => 6,
        };
        buckets[index] += 1.0;
    }

    for bucket in &mut buckets {
        *bucket = (*bucket / total) * 100.0;
    }

    buckets
}

#[pymodule]
fn python_lib(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(solve_poker_spot, m)?)?;
    Ok(())
}
