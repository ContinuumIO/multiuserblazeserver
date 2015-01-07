from nose.tools import with_setup

from mbs.settings import settings
from . import config_file

def setup_function():
    settings.reset()

def teardown_function():
    pass


@with_setup(setup_function, teardown_function)
def test_from_pyfile_no_data_directory():
    old_data_dir = settings.data_directory
    config = config_file("config_no_data_directory.py")
    assert 'data' not in settings.data
    settings.from_pyfile(config)
    assert 'data' in settings.data
    assert settings.data_directory == old_data_dir

@with_setup(setup_function, teardown_function)
def test_from_pyfile_with_data_directory():
    old_data_dir = settings.data_directory
    config = config_file("config_with_data_directory.py")
    assert 'data' not in settings.data
    settings.from_pyfile(config)
    assert 'data' in settings.data
    assert settings.data_directory == '/tmp'
