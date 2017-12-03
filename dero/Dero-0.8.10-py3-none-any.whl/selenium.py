
import selenium, zipfile, os

def apply_proxy_with_authentication_to_chrome_selenium(proxy, port, username, password, directory):
    '''
    Applies a proxy server to Chrome driven by Selenium, with authentication included. This works by
    creating a zip file extension for Chrome which sets the proxy setting and catches prompt
    windows to include username and password info.

    proxy: string, IP or address of your proxy, i.e. 'dubai.wonderproxy.com'
    port: integer, Port for proxy, i.e. 12000
    username: string
    password: string
    directory: string, This should be the wherever you want the zipfile to be placed, i.e. r'C:/Users/John/Desktop'
    '''
    chrome_options = selenium.webdriver.ChromeOptions()
    #self.chrome_options.add_argument('--proxy-server={}'.format(proxy))

    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """

    background_js = '''
    var config = {{
            mode: "fixed_servers",
            rules: {{
              singleProxy: {{
                scheme: "http",
                host: "{0}",
                port: parseInt({1})
              }},
              bypassList: ["foobar.com"]
            }}
          }};

    chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});

    function callbackFn(details) {{
        return {{
            authCredentials: {{
                username: "{2}",
                password: "{3}"
            }}
        }};
    }}

    chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {{urls: ["<all_urls>"]}},
                ['blocking']
    );

    '''.format(proxy,port,username,password)

    plugin_file = os.path.join(directory,'proxy_auth_plugin.zip')

    with zipfile.ZipFile(plugin_file, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)

    chrome_options.add_extension(plugin_file)

    return chrome_options

class AnyEC:
    """ Use with WebDriverWait to combine expected_conditions
        in an OR.
        
    Then call it like...

    from selenium.webdriver.support import expected_conditions as EC
    # ...
    WebDriverWait(driver, 10).until( AnyEC(
        EC.presence_of_element_located(
             (By.CSS_SELECTOR, "div.some_result")),
        EC.presence_of_element_located(
             (By.CSS_SELECTOR, "div.no_result")) ))
        
    """
    def __init__(self, *args):
        self.ecs = args
    def __call__(self, driver):
        for fn in self.ecs:
            try:
                if fn(driver): return True
            except:
                pass