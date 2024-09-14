import python_lib

# Define the inputs
inputs = {
    "Effective stack": 900,
    "Pot before flop": 200,
    "Preflop action": "BTN,SB,BB,SB",
    "Flop Cards": "Td9d6h",
    "Flop bet": 120,  # Example value
    "Turn card": "Qc",
    "Turn bet": 200,  # Example value
    "River card": "7s",
    "River bet": 300,  # Example value
}

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
