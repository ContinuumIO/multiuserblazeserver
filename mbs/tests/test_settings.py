import cStringIO
import tempfile
from os.path import join

from nose.tools import with_setup
from blaze.utils import example

from mbs.settings import settings
from . import config_file, data_file

def setup_function():
    settings.reset()
    settings.data_file = tempfile.mkdtemp()
    datadir = tempfile.mkdtemp()
    settings.data_directory = datadir

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

@with_setup(setup_function, teardown_function)
def test_dataset_storage():
    storage = settings.storage
    assert len(storage) == 0

@with_setup(setup_function, teardown_function)
def test_all_datasets():
    config = config_file("config.py")
    settings.from_pyfile(config)
    settings.data_directory = data_file('datadir')
    all_sets = settings.datamanager.all_datasets()
    assert set(all_sets.keys()) == {'accounts', 'cities', 'events'}

    #now we introduce an error by adding a csv that has tab separators
    settings.datamanager.configure('defaultuser/test.csv', delimiter="|")
    path = join('defaultuser', 'test.hdf5')
    uri1 = 'hdfstore://%s' % path
    settings.datamanager.configure(uri1)
    uri2 = 'hdfstore://%s::temp' % path
    settings.datamanager.configure(uri2)
    all_sets = settings.datamanager.all_datasets()
    assert set(all_sets.keys()) == {'accounts', 'cities', 'events',
                                    join('defaultuser', 'test.csv'),
                                    uri1, uri2
    }
    assert all_sets[uri1]['temp'].shape == (5,1)
    #why is this one a list?!
    assert all_sets[uri2].shape == [5,1]

@with_setup(setup_function, teardown_function)
def test_ls():
    settings.datamanager.write('firstuser', 'foo.hdf5', cStringIO.StringIO())
    settings.datamanager.write('firstuser', 'test.csv', cStringIO.StringIO())
    settings.datamanager.write('seconduser', 'foo2.hdf5', cStringIO.StringIO())
    assert len(settings.datamanager.ls('firstuser')) == 2
    assert len(settings.datamanager.ls()) == 3
