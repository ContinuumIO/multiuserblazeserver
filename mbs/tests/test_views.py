import tempfile
import shutil
from os.path import exists, join
import json

from nose.tools import with_setup

from mbs.app import setup_app
from mbs.settings import settings
from . import config_file, data_file
test = None
data = None
t = None
datadir = None
def setup_function():
    global app
    global test
    global datadir
    global t
    datadir = tempfile.mkdtemp()
    config = config_file("config.py")
    app = setup_app(config_file=config)
    test = app.test_client()
    data = settings.data
    settings.data_directory = datadir

def teardown_function():
    global app
    global test
    global data
    global datadir

    if exists(datadir):
        shutil.rmtree(datadir)

    app = None
    test = None
    data = None
    datadir = None

@with_setup(setup_function, teardown_function)
def test_upload():
    with open(data_file('test.csv')) as f:
        resp = test.post("/upload",
                         data={'file' : (f, 'test.csv')}
                     )
    assert resp.status_code == 200
    result = json.loads(resp.data.decode('utf-8'))
    assert result['path'] == "defaultuser/test.csv"
    assert exists(join(settings.data_directory, result['path']))

@with_setup(setup_function, teardown_function)
def test_upload_without_permissions():
    #monkey patch auth backend to disallow upload
    def reject(path, username):
        return False
    settings.auth_backend.can_write = reject
    with open(data_file('test.csv')) as f:
        resp = test.post("/upload",
                         data={'file' : (f, 'test.csv')}
                     )
    assert resp.status_code == 403
    assert not exists(join(settings.data_directory, "defaultuser", "test.csv"))
