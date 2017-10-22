# This script analyzes the results after performing the following on the command line:
#seq 5 2 25 | xargs -I{} /home/dkoslicki/KhmerVE/bin/python MakeTrainingDatabase.py {}; seq 5 2 25 | xargs -I{} /home/dkoslicki/KhmerVE/bin/python KhmerApproach.py {}
import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib
matplotlib.style.use('ggplot')
ksizes = range(5, 27, 2)

func_of_k = pd.DataFrame()
for ksize in ksizes:
	df = pd.read_csv(os.path.abspath('../data/results-K' + str(ksize) + '.csv'), index_col=0)
	func_of_k = func_of_k.append(pd.DataFrame(df['containment index'].to_dict(), index=[ksize]))

func_of_k.fillna(value=0, inplace=True)

func_of_k.plot()
plt.show()


# Select columns that satisfy condition on last row
df = func_of_k
crit = df.loc[25] > 0
test = df[crit.index[crit]]
plt.figure()
test.plot()
plt.show()

#
