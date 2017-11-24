class ProgressBarB:
	def __init__(self,type=None,object=None,max=None):
		#gives the property of the progressbar
		#type of progressbar
		#object progressbar
		self.typeOfPB=type
		self.object=object
		self.max=max
	
	def initialize(self,max):
		if self.typeOfPB=='ProgressBarView':
			from ProgressBarView import ProgressBarView
			self.object.updateProgress(0,newMax=max)
		elif self.typeOfPB=='ProgressBarText':
			from ProgressBarText import progressbarClass
			self.object=progressbarClass(max)
	
	def progress(self,value):
		if self.typeOfPB=='ProgressBarView':
			from ProgressBarView import ProgressBarView
			self.object.updateProgress(newValue=value)
		elif self.typeOfPB=='ProgressBarText':
			from ProgressBarText import progressbarClass
			self.object.progress(value)

if __name__ == "__main__":
	from time import sleep
	#test avec progress bar
	def test(prbar):
		prbar.initialize(100)
		for i in range(100):
			prbar.progress(i)
			sleep(0.01)
	
	pb=ProgressBarB(type='ProgressBarText',max=100)
	test(pb)
	from Tkinter import *
	from ProgressBarView import *
	root=Tk()
	root.title("Progress bar!")
	label = Label(root, text='Progress bar:', anchor=NW, justify=LEFT, width=30)
	label.pack(fill=X, expand=1)
	#bar = ProgressBarView(root, value=33, orientation="vertical", height=200)
	bar = ProgressBarView(root, value=33)
	bar.pack(fill=X)
	sleep(0.2)
	bar.updateProgress(20)
	pb2=ProgressBarB(type='ProgressBarView',object=bar)
	test(pb2)
	root.mainloop()