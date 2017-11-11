import requests
import json

data = {
    'html': '<div>Hello world</div>',
    'title': 'new Pen'
}

payload = {'data': json.dumps(data)}
r = requests.post('http://codepen.io/pen/define', data=payload)

