import io


def render(data, out_write):
    out_write('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"\n          "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">\n <head>\n  <title>Stock Prices</title>\n  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />\n  <meta http-equiv="Content-Style-Type" content="text/css" />\n  <meta http-equiv="Content-Script-Type" content="text/javascript" />\n  <link rel="shortcut icon" href="/images/favicon.ico" />\n  <link rel="stylesheet" type="text/css" href="/css/style.css" media="all" />\n  <script type="text/javascript" src="/js/util.js"></script>\n  <style type="text/css">\n  /*<![CDATA[*/\nbody {\n    color: #333333;\n    line-height: 150%;\n}\nthead {\n    font-weight: bold;\n    background-color: #CCCCCC;\n}\n.odd {\n    background-color: #FFCCCC;\n}\n.even {\n    background-color: #CCCCFF;\n}\n.minus {\n    color: #FF0000;\n}\n  /*]]>*/\n  </style>\n\n </head>\n\n <body>\n\n  <h1>Stock Prices</h1>\n\n  <table>\n   <thead>\n    <tr>\n     <th>#</th><th>symbol</th><th>name</th><th>price</th><th>change</th><th>ratio</th>\n    </tr>\n   </thead>\n  <tbody>\n')  # noqa
    for i, item in enumerate(data['stocks']):
        out_write('\n    <tr class="')
        out_write('odd' if (i % 2 == 0) else 'even')
        out_write('">\n     <td style="text-align: center">')
        out_write(str(i))
        out_write('</td>\n     <td>\n      <a href="/stocks/')
        out_write(item['symbol'])
        out_write('">')
        out_write(item['symbol'])
        out_write('</a>\n     </td>\n     <td>\n      <a href="')
        out_write(item['url'])
        out_write('">')
        out_write(item['name'])
        out_write('</a>\n     </td>\n     <td>\n      <strong>')
        out_write(str(item['price']))
        out_write('</strong>\n     </td>\n    ')
        if item['change'] < 0.0:
            out_write('\n     <td class="minus">')
            out_write(str(item['change']))
            out_write('</td>\n     <td class="minus">')
            out_write(str(item['ratio']))
            out_write('</td>\n    ')
        else:
            out_write('\n     <td>')
            out_write(str(item['change']))
            out_write('</td>\n     <td>')
            out_write(str(item['ratio']))
            out_write('</td>\n    ')
        out_write('\n    </tr>\n')
    out_write('\n</tbody>\n  </table>\n\n </body>\n</html>\n')


def render_io(data):
    with io.StringIO() as out:
        out.truncate(2048)
        out.seek(0)
        out_write = out.write
        render(data, out_write)
        return out.getvalue()


def render_join(data):
    out = []
    out_write = out.append
    render(data, out_write)
    return ''.join(out)
