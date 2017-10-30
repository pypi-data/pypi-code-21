def eq(code, **kwargs):
	from matplotlib.figure import Figure
	import matplotlib.pyplot as plt
	plt.rc('text', usetex=True)
	plt.rc('font', family='serif')
	if "horizontalalignment" not in kwargs:
		kwargs["horizontalalignment"] = "center"
	if "verticalalignment" not in kwargs:
		kwargs["verticalalignment"] = "center"
	f = Figure(frameon=False)
	f.text(0.5, 0.5, code, **kwargs)
	return f