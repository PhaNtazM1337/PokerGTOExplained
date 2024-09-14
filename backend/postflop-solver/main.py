import python_lib

# Define the inputs

def process(inputs):

    # inputs = {
    #     "effective_stack": 900,
    #     "pot_before_flop": 200,
    #     "preflop_action": "BTN,SB,BB,SB",
    #     "flop_cards": "Td9d6h",
    #     "flop_bet": 120,  # Example value
    #     "turn_card": "Qc",
    #     "turn_bet": 200,  # Example value
    #     "river_card": "7s",
    #     "river_bet": 300,  # Example value
    # }

    # Call the solver function
    result = python_lib.solve_poker_spot(inputs)

    # Access the results
    hero_ranges = result["Hero"]
    villain_ranges = result["Villain"]
    hero_buckets = result["Hero Equity Buckets"]
    villain_buckets = result["Villain Equity Buckets"]
    legal_actions = result["Legal Actions"]

    # Print the results
    print(result)

    # 
    return result
