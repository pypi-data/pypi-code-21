# by lich666dead
#email lich666black@gmail.com
import os, json

class Phantomjs():
        core = False

        def __init__( self, url, interval = 1000, userAgent = None, js = [], image = False , proxies = None, command = 'phantomjs', param = None):
                if param != None:
                    self.settings = param
                else:
                    self.settings = {
                        'image': { 'width': 1920, 'height': 1024, 'loadImages': image, 'image_name': 'basilisk' },
                        'userAgent': '' if userAgent == None else userAgent,
                        'js': str( js ),
                        'url': url,
                        'interval': str( interval ),
                        'command':command,
                        'proxies': 'page.setProxy("%s");' %proxies if proxies != None else ''
                        # http://user:pass@proxy_ip_or_host:port/
                        }

        @staticmethod
        def write_( node ):
                with open( 'run.js', 'w' ) as f:
                        f.write( node )

        @staticmethod
        def node():
                return '''var page = new WebPage(), testindex = 0, loadInProgress = false;
page.settings.userAgent = 'userAgentSet';
system = require('system');
page.viewportSize = { width: setWidth, height: setHeight };
page.settings.loadImages = false;
var data = {};
page.setProxy("SET_proxies");
var js_array = js_pool_set_array;
page.onConsoleMessage = function(msg) {
  console.log(msg);
};
page.onNavigationRequested = function() {
	loadInProgress = true;
}
page.onLoadStarted = function() {
  loadInProgress = true;

};
page.onLoadFinished = function() {
  loadInProgress = false;
};
var steps = [
  function() {
    page.open('url_set', function(status) {
  data['status'] = status;
  });
  },
  function() {
  for (var i = 0; i < js_array.length; i++) {
    data[i] = page.evaluateJavaScript("function(){ try { return " + js_array[ i ] + "; } catch (e) {} finally {}; }")
  }
  }
];
interval = setInterval(function() {
  if (!loadInProgress && typeof steps[testindex] == "function") {
    steps[testindex]();
    testindex++;
  }
  if (typeof steps[testindex] != "function") {
    if ( system.args[ 1 ] == 'True') {
       data['content'] = page.content;
    }
    if ( system.args[ 2 ] == 'True') {
       page.render( 'Set_Image_Name.png' );
    }
    data['url'] = page.url;
    console.log(JSON.stringify(data));
    phantom.exit();
  }
}, set_interval_time);
'''

        @staticmethod
        def run( command ):
                with os.popen( command ) as j:
                        for i in j.read().split('\n'):
                                try:
                                        return json.loads( i )
                                except:
                                        continue

        def read_node( self ):
                node = self.node()\
                       .replace('url_set', self.settings['url'] )\
                       .replace('userAgentSet', self.settings['userAgent'])\
                       .replace('setWidth', str(self.settings['image']['width']))\
                       .replace( 'setHeight', str(self.settings['image']['height']))\
                       .replace( 'loadImages_this_set', 'false' if not self.settings['image'][ 'loadImages' ] else 'true')\
                       .replace( 'js_pool_set_array', self.settings['js'] )\
                       .replace( 'set_interval_time', self.settings['interval'] )\
                       .replace( 'Set_Image_Name', self.settings[ 'image' ]['image_name'] )\
                       .replace( 'page.setProxy("SET_proxies");', self.settings[ 'proxies' ] )
                self.write_(node)
                self.core = True

        def get( self, content = False, screenshot = False ):
                if not self.core:self.read_node()
                return self.run( self.settings['command'] + ' run.js ' + str( content ) + ' ' + str( screenshot ) )