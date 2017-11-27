from xml.etree import ElementTree as E

SUBMIT = E.fromstring(b'<button type="submit">Run</button>')

def form(function, method, arguments, message, output):
    '''
    :param dict Configuration flatconf: Flattened configuration,
        with function call input values
    :param Function func: Function for the given endpoint
    :param bool with_help: Include help text
    :param str output: Program output
    '''
    if not isinstance(output, str):
        raise TypeError('Form output must be str')
    m = E.Element('textarea', **{'readonly': '', 'class': 'message list-box-row'})
    if message:
        m.text = str(message)

    i = E.Element('form', method=method, enctype='multipart/form-data', action='')
    for param in function.all_parameters():
        try:
            element = param.dumps('wsgi', param.default)
        except Exception as e:
            logger.exception('Failed to dump value for %s' % param.name)
        else:
            i.append(element)
    i.append(SUBMIT)

    o = E.Element('textarea', **{'readonly': '', 'class': 'output list-box-row'})
    if output:
        o.text = output

    main = E.Element('main', role='main')
    main.append(m)
    main.append(i)
    main.append(o)
    return E.tostring(main, method='html').decode('utf-8')

default_template = '''\
<!DOCTYPE html>
<html>
  <head>
    <title>${title}</title>
    <meta content="${description}" name="description">
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <meta charset="utf-8">
    <meta content="horetu" name="generator">
    <meta content="${author}" name="author">
    <style>
      .list-box-row {
        width: 640px;
        display: block;
      }
      .list-box-row > * { padding: 0.25em; margin: 0.25em; }

      .message { height: 2em; color: red; }
      .message, .output { background-color: #eee; }
      .output { margin-top: 1em; height: 6em; }

      /* Single-row field */
      .list-box-row.oneline label { float: left; }
      .list-box-row.oneline { height: 4em; }
      .list-box-row.oneline input, .list-box-row.oneline select
        { height: 3em; float: right; }

      /* Multi-row field */
      .list-box-row.multiline { height: 8em; }
      .list-box-row textarea { display: block; height: 6em; }
    </style>
  </head>
  <body>${body}</body>
</html>
'''
