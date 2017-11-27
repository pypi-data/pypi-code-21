import os
import urllib.request
from urllib.error import HTTPError
from urllib.parse import (
    urlparse, urljoin, quote, urlunparse)
import string

customize_headers = {}
customize_url = []
customize_num = 0



def getheaders(url, timeout=60, host="", urlonly=False,
                   user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'):
    global customize_headers
    global customize_num
    global customize_url




    try:
       class MyRedirectHandler(urllib.request.HTTPRedirectHandler):
            max_repeats = 4
            max_redirections = 10

            def http_error_302(self, req, fp, code, msg, headers):
                # Some servers (incorrectly) return multiple Location headers
                # (so probably same goes for URI).  Use first header.
                global customize_headers
                global customize_num
                global customize_url

                customize_headers[customize_num] = dict(headers)
                customize_num = customize_num +1

                if "location" in headers:
                    newurl = headers["location"]
                    customize_url.append(headers["location"])

                elif "uri" in headers:
                    newurl = headers["uri"]
                    customize_url.append(headers["uri"])
                else:
                    return

                # fix a possible malformed URL
                urlparts = urlparse(newurl)

                # For security reasons we don't allow redirection to anything other
                # than http, https or ftp.

                if urlparts.scheme not in ('http', 'https', 'ftp', ''):
                    raise HTTPError(
                        newurl, code,
                        "%s - Redirection to url '%s' is not allowed" % (msg, newurl),
                        headers, fp)

                if not urlparts.path and urlparts.netloc:
                    urlparts = list(urlparts)
                    urlparts[2] = "/"
                newurl = urlunparse(urlparts)

                # http.client.parse_headers() decodes as ISO-8859-1.  Recover the
                # original bytes and percent-encode non-ASCII bytes, and any special
                # characters such as the space.
                newurl = quote(
                    newurl, encoding="iso-8859-1", safe=string.punctuation)
                newurl = urljoin(req.full_url, newurl)

                # XXX Probably want to forget about the state of the current
                # request, although that might interact poorly with other
                # handlers that also use handler-specific request attributes
                new = self.redirect_request(req, fp, code, msg, headers, newurl)
                if new is None:
                    return

                # loop detection
                # .redirect_dict has a key url if url was previously visited.
                if hasattr(req, 'redirect_dict'):
                    visited = new.redirect_dict = req.redirect_dict
                    if (visited.get(newurl, 0) >= self.max_repeats or
                                len(visited) >= self.max_redirections):
                        raise HTTPError(req.full_url, code,
                                        self.inf_msg + msg, headers, fp)
                else:
                    visited = new.redirect_dict = req.redirect_dict = {}
                visited[newurl] = visited.get(newurl, 0) + 1

                # Don't close the fp until we are sure that we won't use it
                # with HTTPError.
                fp.read()
                fp.close()

                return self.parent.open(new, timeout=req.timeout)

            http_error_301 = http_error_303 = http_error_307 = http_error_302

            inf_msg = "The HTTP server returned a redirect error that would " \
                      "lead to an infinite loop.\n" \
                      "The last 30x error message was:\n"

       myHandler = MyRedirectHandler()
       opener = urllib.request.build_opener(myHandler)

       headers = {'User-Agent': user_agent}
       req = urllib.request.Request(url, headers=headers)
       response = opener.open(req, timeout=timeout)

       if urlonly:
           return customize_url
           customize_headers = {}
           customize_url = []
           customize_num = 0
           return customize_url

       else:
           return customize_headers
           customize_headers = {}
           customize_url = []
           customize_num = 0





    except Exception as e:
        return "system error: " + str(e)








