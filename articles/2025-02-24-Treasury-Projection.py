depletion = 0.115
inflow = 0.04

year = 2025
reserves = 7_495_773_911_585_373
treasury = 1_641_656_329_184_830
withdrawals = 300_000_000_000_000

print("| Year ", end="")
print("| Reserves                   ", end="")
print("| Treasury                   ", end="")
print("| Withdrawals/Inflow       ", end="")
print("|")
print("|------", end="")
print("|---------------------------:", end="")
print("|---------------------------:", end="")
print("|-------------------------:", end="")
print("|")
print(f"| {year} ", end="")
print(f"| {reserves:21_d} µADA ", end="")
print(f"| {treasury:21_d} µADA ", end="")
print(f"| {withdrawals:19_d} µADA ", end="")
print("|")

for _ in range(8):
    year += 1
    reserves_diff = int(-reserves * depletion)
    treasury_inflow = int(reserves * inflow)
    treasury_diff = treasury_inflow - withdrawals
    reserves += reserves_diff
    treasury += treasury_diff
    print(f"|      ", end="")
    print(f"| {reserves_diff:+21_d} µADA ", end="")
    print(f"| {treasury_diff:+21_d} µADA ", end="")
    print(f"| {treasury_inflow:19_d} µADA ", end="")
    print("|")
    print(f"| {year} ", end="")
    print(f"| {reserves:21_d} µADA ", end="")
    print(f"| {treasury:21_d} µADA ", end="")
    print(f"| {withdrawals:19_d} µADA ", end="")
    print("|")
