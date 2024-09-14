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

    # Print the results
    print("Hero Ranges:")
    for hand, info in hero_ranges.items():
        print(f"{hand}: EV={info['EV']}, Equity={info['Equity']}, EQR={info['EQR']}")

    print("\nVillain Ranges:")
    for hand, info in villain_ranges.items():
        print(f"{hand}: EV={info['EV']}, Equity={info['Equity']}, EQR={info['EQR']}")

    print("\nHero Equity Buckets:")
    print(hero_buckets)

    print("\nVillain Equity Buckets:")
    print(villain_buckets)

    return result
