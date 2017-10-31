#!/usr/bin/env python

from bondcomp import bondcomp

bond_maturity_date = input("When does this bond mature? (Format: MM/DD/YYYY):" )

date_elements = bond_maturity_date.split('/')

month, day, year = int(date_elements[0]), int(date_elements[1]), int(date_elements[2])

ytm = bondcomp.years_to_maturity(year,month,day)
ust_benchmark = bondcomp.ust_benchmark_select(ytm)

print("Years to Maturity: {0:.3}".format(ytm))
print("US Treasury Benchmark: {}".format(ust_benchmark))
