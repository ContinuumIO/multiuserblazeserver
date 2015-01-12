import json

import requests
from six import string_types

#probably to be wrapped by some stateful client object

#request session
s = None
def _session():
    global s
    if s is None:
        s = requests.session()
    return s

def _reset_session():
    global s
    s = None

def sanitize_url(url):
    if not url.endswith("/"):
        url += "/"
    return url

class MBSClientException(Exception):
    pass

def _request(method, url, data=None, files=None, headers=None, session=None):
    if session is None:
        session = _session()
    resp = session.request(method, url, data=data, files=files, headers=headers)
    if resp.status_code != 200:
        raise MBSClientException(resp.status_code)
    else:
        return resp.json()

def register(root_url, username, password, session=None):
    raise NotImplementedError

def login(root_url, username, password, session=None):
    raise NotImplementedError

def upload(root_url, file_or_path, session=None):
    url = sanitize_url(root_url) + "upload"
    if isinstance(file_or_path, string_types):
        with open(file_or_path, 'rb') as f:
            _request('POST', url, files={'file' : f})
    else:
        _request('POST', url, files={'file' : file_or_path})

def ls(root_url, username=None):
    root_url = sanitize_url(root_url)
    if username:
        url =  root_url + "ls/%s" % username
    else:
        url = root_url + "ls"
    return _request('GET', url)

def configure(root_url, uri, _delete=False, **kwargs):
    url = sanitize_url(root_url) + "configure"
    data = json.dumps(dict(uri=uri, kwargs=kwargs, _delete=_delete))
    return _request('POST', url, data=data,
                    headers={'content-type' : 'application/json'})
