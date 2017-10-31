"""
Calculates the years to maturity and selects the appropriate UST benchmark.
"""
import datetime

# Calculates years to maturity from today as a float
def years_to_maturity(year,month,day, day_count = 360):
    today = datetime.datetime.today()
    maturity = datetime.datetime(year,month,day)
    years2mat = ((maturity - today).days)/day_count
    years2mat = round(years2mat,3)
    return years2mat

# determines the closest US Treasury benchmark, below the final maturity.
def ust_benchmark_select(years):
    ust_benchmarks = (0,1,2,3,5,7,10,30)
    potential_benchmarks = [n for n in ust_benchmarks if n <= years]
    # if len(potential_benchmarks) < 2:
    #     print("The benchmark is less than 2 years.")
    return max(potential_benchmarks)
