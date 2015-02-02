import os
import time
from os.path import getmtime, exists, abspath, join
import shelve
import imp
import uuid
import copy
import logging

from .auth import SingleUserAuthenticationBackend
from .datamanager import DataManager

logger = logging.getLogger(__name__)

defaults = dict(
    data_directory=join(os.getcwd(), "mbsdata"),
    data={},
    multi_user=False,
    ip="0.0.0.0",
    port=6039,
    url_prefix="",
    data_file='data.db',
    auth_backend=SingleUserAuthenticationBackend(admin=True)
)

class Settings(object):
    bp_settings = ['data_directory', 'data', 'multi_user',
                   'auth_backend', 'data_file']
    app_settings = ['ip', 'port', 'url_prefix']

    def __init__(self):
        self._storage = None
        self._datamanager = None

    def reset(self):
        for k,v in defaults.items():
            setattr(self, k, copy.copy(v))
        self.close_storage()

    def postprocess(self):
        self.data_directory = abspath(self.data_directory)
        if not exists(self.data_directory):
            os.makedirs(self.data_directory)
        self.data_file = abspath(self.data_file)

    def close_storage(self):
        if self._storage is not None:
            self._storage.close()
        self._storage = None
        self._storage_time = 0

    def from_pyfile(self, fname):
        name = "_mbs_configuration"
        mod = imp.load_source(name, fname)
        for k in self.bp_settings:
            v = getattr(mod, k, None)
            if v is not None:
                setattr(self, k, v)
        for k in self.app_settings:
            v = getattr(mod, k, None)
            if v is not None:
                setattr(self, k, v)
        self.postprocess()

    @property
    def storage(self):
        """where we store metadata about uploaded datasets
        """
        if self._storage is None:
            self._storage = shelve.open(self.data_file, protocol=-1)
        self._storage.sync()
        return self._storage

    @property
    def datamanager(self):
        if self._datamanager is None:
            self._datamanager = DataManager(self)
        return self._datamanager

settings = Settings()
settings.reset()
del Settings
