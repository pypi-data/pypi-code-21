import pandas as pd
import scipy.stats as st

def chiSquare(data, x=None, y=None, margins=False):


	dataChi = data[[x, y]].dropna()

	crossT = pd.crosstab(dataChi[x], dataChi[y], margins=False)

	print('\n#' + '-'*60 + '#')
	print('#'*20 + ' Chi-Square Test ' + '#'*20 + '\n')
	print('x : ' + x)
	print('y : ' + y)
	print('\n## Contingency Table')
	print('-'*50)
	print(crossT)
	print('-'*50)

	chiSqr, pValue, freeDeg, expectedV = st.chi2_contingency(crossT)
	expectedV = pd.DataFrame(expectedV, index=crossT.index.copy(), columns=crossT.columns.copy())

	msg = '## Test Statistic : {}\n## P-value : {}\n## Degrees of Freedom : {}'

	print('\n\n' + msg.format( chiSqr, pValue, freeDeg ) )
	print('\n' + '## Expected Values')
	print('-'*60)
	print( expectedV )
	print('-'*60)
	print('#' + '-'*60 + '#\n')

	return crossT, chiSqr, pValue, freeDeg, expectedV



