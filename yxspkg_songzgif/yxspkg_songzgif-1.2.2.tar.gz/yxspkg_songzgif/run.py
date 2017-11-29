import sys
import yxspkg_songzviewer
def gif_run():
	from . import gif 
	gif.main()
if __name__=='__main__':

	if len(sys.argv)!=1:
		yxspkg_songzviewer.main() 
	else:
		gif_run()