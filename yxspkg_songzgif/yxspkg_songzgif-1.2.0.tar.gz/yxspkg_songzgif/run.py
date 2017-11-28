import sys
def gif_run():
	from . import gif 
	gif.main()
def viewer_run():
	import yxspkg_songzviewer 
	yxspkg_songzviewer.main()
if len(sys.argv)!=1:
	viewer_run()
else:
	gif_run()