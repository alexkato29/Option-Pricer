from EuropeanOption import *

# (type, underlying, strike, days to exp, rate, div, vol (optional), price (optional), debug)
option1 = Option("call", 100, 100, 30, 2, 0, 0, 4.65)

print(option1.vol)
