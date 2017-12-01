import webbrowser, urllib, collections, requests, urllib, base64, tempfile, time, sys
import json as lib_json
use_ipython = False
try:
    from IPython.core.display import display, HTML
    from IPython import get_ipython
    from IPython.display import clear_output
    use_ipython = True
except ImportError:
    pass
from cryptography.hazmat.primitives import serialization, hashes, asymmetric
from cryptography.hazmat.backends import default_backend

import_numpy_err = None
try:
    import numpy as np
    import scipy.stats
except ImportError as e:
    import_numpy_err = e

import_pandas_err = None
try:
    import pandas
except ImportError as e:
    import_pandas_err = e
    
try:
    # module from Python 3.6
    from secrets import token_urlsafe
except ImportError:
    import string, random
    def token_urlsafe(nbytes=6):
            chars = string.ascii_lowercase + string.ascii_uppercase + string.digits
            return ''.join(random.choice(chars) for _ in range(nbytes))

button_css = '''
a.autograder.login {
  font-size: 130%;
  display: inline-block;
  padding: 0.15em 0.4em; margin-bottom: 0;
  border-radius: 0.3em;
  color: white;
  background-color: #337ab7;
  border: 1px solid transparent;
  border-color: #2e6da4;
  font-weight: normal; text-align: center; vertical-align: middle;
  cursor: pointer;
  white-space: nowrap;
  text-decoration: none;
  }}
a.autograder.login:hover {{
  background-color: #286090;
  border-color: #204d74;
  }
'''
        
def autograder(url, course, section=None, timeout=25):
    key = asymmetric.rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend())
    nonce = token_urlsafe(nbytes=30)
    prefix = '/'.join(s for s in [course,section] if s is not None)
    grader = Autograder(url=url, prefix=prefix, key=key, nonce=nonce)

    login_parameters = {'url': grader.url + 'login/raven/',
                        'signing_key': urllib.parse.quote(grader.signing_key_pem),
                        'show': '&show='+prefix if prefix else ''
                       }
    if not (use_ipython and get_ipython()):
        webbrowser.open('{url}?{show}&signing_key={signing_key}'.format(**login_parameters))
    else:
        html = r'''
        <style type="text/css">{css}</style>
        <div>
       <a class='autograder login' href="{url}?{show}&signing_key={signing_key}" target="grader_login">log in</a>
        </div>
        '''.format(css=button_css, **login_parameters)
        display(HTML(html))
    
    sys.stdout.flush()
    t0 = time.time()
    last_dot = t0
    shown_start = False
    authenticated = False
    msg = ''
    while time.time() < t0 + timeout:
        if not shown_start and time.time() > t0 + 2:
            msg = 'Waiting for you to log in ..'
            print(msg, end='')
            shown_start = True
            last_dot = time.time()
        if time.time() > last_dot + 2:
            print(".", end='')
            msg = msg + '.'
            sys.stdout.flush()
            last_dot = time.time()
        if grader.ready(verbose=False):
            authenticated = True
            break
        time.sleep(0.5)
    if authenticated:
        if use_ipython and get_ipython():
            clear_output()
            print(msg, 'done.')
        else:
            print(' done')
        return grader
    else:
        if use_ipython and get_ipython():
            clear_output()
            print(msg, " still waiting.")
        else:
            print("not yet authenticated.")
        return grader


class Autograder(object):
    def __init__(self, url, prefix, key, nonce):
        if url[-1] != '/':
            url = url + '/'
        if prefix and prefix[-1] != '/':
            prefix = prefix + '/'
        if prefix == '/':
            raise ValueError("Empty course/section")
        self.url = url
        self.prefix = prefix 
        self.key = key      # stored in notebook
        self.nonce = nonce  # only in Python, not in notebook

    def subsection(self, prefix):
        return Autograder(self.url, self.prefix + prefix, self.key, self.nonce)
    def for_course(self, course, section=None):
        prefix = '/'.join(s for s in [course,section] if s is not None)
        return Autograder(self.url, prefix, self.key, self.nonce)
        
    @property
    def signing_key_pem(self):
        return self.key.public_key().public_bytes(
            encoding = serialization.Encoding.PEM,
            format = serialization.PublicFormat.SubjectPublicKeyInfo)
    @property
    def cookies(self):
        return {'signing_key': urllib.parse.quote(self.signing_key_pem),
                'nonce': urllib.parse.quote(self.nonce)}

    def ready(self, verbose=True):
        status = requests.get(self.url + 'ping/', cookies=self.cookies).status_code
        if verbose and status == 401:
            print("Not logged in")
        return status == 200
    
    def fetch_question(self, label):
        r = requests.get(self.url + 'fetch_question/' + self.prefix + label, cookies=self.cookies)
        if r.status_code == 404:
            raise KeyError(self.prefix + label)
        elif r.status_code == 403:
            raise ConnectionRefusedError(r.reason)
        elif r.status_code != 200:
            raise Exception("Unable to fetch question ({}): {}".format(r.status_code, r.reason))
        return SetQuestion(r.json())

    def post_with_signature(self, url, message:bytes):
        assert isinstance(message, bytes), "Signed messages must be in bytes"
        signature = self.key.sign(
            data = message,
            padding = asymmetric.padding.PSS(
                mgf = asymmetric.padding.MGF1(hashes.SHA256()),
                salt_length = asymmetric.padding.PSS.MAX_LENGTH),
            algorithm = hashes.SHA256())
        # To get the message_bytes through safely, I'll base64-encode, then send as ascii/string. 
        json_enc = {'message': base64.b64encode(message), 'signature':base64.b64encode(signature)}
        r = requests.post(url, cookies=self.cookies, data=json_enc)
        if r.status_code == 400:
            raise Exception("Internal error in ucamcl package: {}".format(r.reason))
        elif r.status_code == 401:
            raise ConnectionRefusedError("Error: {}\nPlease re-authenticate and try again".format(r.reason))
        elif r.status_code >= 500 and r.status_code < 600:
            raise Exception("Server error: {}\nPlease try again later.".format(r.text[:1000]))
        else:
            return r

    def submit_answer(self, q, ans):
        message = lib_json.dumps({'answer': jsonable(ans), 'question_id': q.id}).encode('utf8')
        r = self.post_with_signature(self.url + 'submit_answer/', message)
        if r.status_code == 403:
            print("Please fetch the question before submitting an answer")
            return (None,{})
        elif r.status_code == 405:
            print("No answer is expected")
            return (None,{})
        elif r.status_code != 200:
            raise Exception("Unexpected error: {}".format(r.text[:1000]))
        res = r.json()
        if res['correct'] == True:
            print("Correct!")
        elif res['correct'] == False:
            print("Incorrect")
        else:
            print("The question is stale. Please re-fetch and try again")
        return res['correct'], res['answer']

    def set_question(self, label, parameters=None, answer=None, description=None, tag=None):
        '''Store a question.
        parameters=None, answer=None: no answer is expected; the description is all
        parameters=None, answer=a: there is only one answer
        parameters=[p1,..,pn], answers=[a1,..,an]: a parameterized question
        '''
        if parameters is None and answer is None:
            return self._set_question(label, [None], [None], description, tag)
        elif parameters is None and answer is not None:
            return self._set_question(label, [{}], [answer], description, tag)
        elif parameters is not None:
            if len(parameters) != len(answer):
                raise ValueError("parameters and answer should be the same length")
            if not all(isinstance(p,dict) for p in parameters):
                raise ValueError("Each element of parameters should be a dict")
            return self._set_question(label, parameters, answer, description, tag)
        else:
            raise Exception("Logic failure")

    def delete_question(self, label):
        return self._set_question(self, label, [], [], None, None)
        
    def _set_question(self, label, parameters, answer, description, tag):
        j = {'parameters':parameters, 'answer': [jsonable(a) for a in answer]}
        if description is not None:
            j['description'] = description.strip()
        if tag is not None:
            j['tag'] = tag.strip()
        msg = lib_json.dumps(j).encode('utf8')
        r = self.post_with_signature(self.url + 'set_question/' + self.prefix + label, msg)
        if r.status_code == 403:
            raise Exception("Authorization error: {}".format(r.reason))
        elif r.status_code != 200:
            raise Exception("Unexpected error: {}".format(r.text[:1000]))
        res = r.json()
        if res.get('num_deleted', 0) > 0:
            print("Deleted", res['num_deleted'], "unused versions")
        return Question(label=res['label'], question_id=res['question_id'], description=res['description'], tag=res['tag'])

    def set_title(self, label='', description='', url=''):
        j = {'description': description, 'url': url}
        msg = lib_json.dumps(j).encode('utf8')
        r = self.post_with_signature(self.url + 'set_title/' + self.prefix + label, msg)
        if r.status_code == 403:
            raise Exception("Authorization error: {}".format(r.reason))
        elif r.status_code != 200:
            raise Exception("Unexpected error: {}".format(r.text[:1000]))
        res = r.json()
        return Question(label=res['label'], question_id=None, description=res['description'], tag=None)

    
Question = collections.namedtuple('Question', ['label', 'question_id', 'description', 'tag'])

class SetQuestion:
    def __init__(self, qspec):
        self.label = qspec['label']
        self.description = qspec['description']
        self.id = qspec['id']
        param_str = qspec['parameters']
        self._parameters = lib_json.loads(param_str) if param_str is not None else {}
    def __getattr__(self, key):
        if self._parameters is None:
            raise AttributeError(key)
        try:
            return self._parameters[key]
        except KeyError as e:
            raise AttributeError(key)
    def __iter__(self):
        return iter(self._parameters)
    def keys(self):
        return self._parameters.keys()
    def items(self):
        return self._parameters.items()
    def __len__(self):
        return len(self._parameters)
    def __repr__(self):
        res = []
        if self._parameters:
            for k,v in self._parameters.items():
                res.append("{k} = {v}".format(k=k, v=v))
        if self.description:
            res.append(self.description.strip())
        return '\n'.join(res)


class Samples:
    def __init__(self, x):
        self._list = [x]
    def append(self, x):
        self._list.append(x)
        return self
    def conf(self, conf, scalar_conf):
        if len(set(self._list)) == 1:
            return scalar_conf(self._list[0])
        x = np.array(self._list)
        q05,med,q95 = np.percentile(x, q=[5, 50, 95])
        r = max(q95-med, med-q05)
        r = scipy.stats.norm.ppf(1-(1-conf)/2) / scipy.stats.norm.ppf(.95) * r
        fudge = 2  # in case the data is skewed...
        return {'_value': med, '_err': ['+', fudge * r]}


def add_sample(x, xs=None):
    if xs is None:
        if isinstance(x, dict):
            return {k: add_sample(v, None) for k,v in x.items()}
        elif isinstance(x, list):
            return [add_sample(v, None) for v in x]
        else:
            return Samples(x)
    else:
        if isinstance(x, dict):
            return {k: add_sample(x[k], v) for k,v in xs.items()}
        elif isinstance(x, list):
            return [add_sample(x[i], v) for i,v in enumerate(xs)]
        else:
            return xs.append(x)

        
def close_enough(*args, conf=0.999, rep=20, tolerance=0.00001):
    if import_numpy_err is not None:
        raise import_numpy_err

    def scalar_conf(x):
        return {'_value': x, '_err': ['+', x*tolerance]} if isinstance(x, float) else x
    
    def obj_conf(samples):
        if isinstance(samples, dict):
            return {k: obj_conf(v) for k,v in samples.items()}
        elif isinstance(samples, list):
            return [obj_conf(v) for v in samples]
        elif isinstance(samples, np.ndarray):
            return obj_conf(samples.tolist())
        elif isinstance(samples, Samples):
            return samples.conf(conf, scalar_conf)
        else:
            return scalar_conf(samples)

    def dec(f):
        def foo(*args, **kwargs):
            samples = None
            for _ in range(rep):
                samples = add_sample(f(*args, **kwargs), samples)
            return obj_conf(samples)
        return foo
    if len(args) == 0:
        return dec
    elif len(args) == 1:
        f = args[0]
        return dec(f) if callable(f) else obj_conf(f)
    else:
        raise Exception("This function takes one positional argument")


def jsonable(x):
    '''Clean any non-json things and make them json-able'''
    if import_numpy_err is None:
        if isinstance(x, np.ndarray):
            return x.tolist()
    if import_pandas_err is None:
        if isinstance(x, pandas.DataFrame):
            i = np.lexsort([x[col] for col in reversed(x.columns)])
            return x.iloc[i].to_dict('records')
    return a
    
