from statsmodels.stats.outliers_influence import variance_inflation_factor as sv

def vif(data, thresh=5.0):

	dropped = True
	
	while dropped == True :
		variables = list(range(data.shape[1])

		dropped = False
		
		vifTable = [sv(data[variables].values, col) for col in range(data[variables].shape[1])]

		maxLoc = vifTable.index(max(vifTable))

		if max(vifTable) >= thresh:

			print('Dropping \'' + data[variables].columns[maxLoc] + '\' at index: ' + str(maxLoc))

			data = data.drop(data.columns[maxLoc], axis=1)
			del variables[maxLoc]

			dropped = True

	print('Remaining Variables')
	print(data.columns[variables])

	return data[variables].columns, data[variables]
