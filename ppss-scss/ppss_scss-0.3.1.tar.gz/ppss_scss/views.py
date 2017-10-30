from pyramid.view import view_config
from pyramid.response import Response,FileResponse
import sass

from ppss_scss import routepath,sourcedir,workingfolder
import os
import logging
l = logging.getLogger(__name__)

class PPSSViews():
    
    def __init__(self,request):
        self.request = request
    

    def createCSSPath(self):
        pass

    def createSCSSPath(self):
        pass

    @view_config(route_name='ppss_scss_compile')
    def servescss(self):
        #print "serve scss!!!!"
        cu = self.request.current_route_url()
        path = self.request.current_route_path()
        fizzle = list(self.request.matchdict.get('fizzle'))
        filename = fizzle[-1]
        if filename[-4:].lower() != ".css":
            return Response("Invalid extension",status_code=404)
        returnfilepath = os.path.join( workingfolder, "/".join(fizzle) )
        
        if not os.path.isfile(returnfilepath ):
            fizzle[-1]=fizzle[-1][:-4] +".scss"
            l.debug("++++ '{fz}'".format(fz=fizzle) )
            #print "++++ '{fz}'".format(fz=fizzle)
            srcfname = os.path.join(sourcedir,*fizzle)
            l.info("+++SCSS compile src='{fn}'".format(fn=srcfname))
            #print "+++SCSS compile src='{fn}'".format(fn=srcfname)
            css = sass.compile_file( str(srcfname) )
            with open( returnfilepath,'w'  ) as outputfile:
                outputfile.write(css)
        else:
            l.debug("Serving {file} from cache".format(file=returnfilepath) )
        return FileResponse(
            returnfilepath,
            request=self.request,
            content_type='text/css'
        )

        fname = os.path.join(sourcedir,*fizzle)
        if os.path.isfile(fname):
            r = Response(content_type='application/csv')
            response.app_iter = exp.writeAll()
            response.headers['Content-Disposition'] = ("attachment; filename=export.csv")
            return response 
        return Response('ok')