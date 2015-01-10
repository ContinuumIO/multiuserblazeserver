from os.path import join, dirname, exists, relpath
import time
import os
import copy
import logging

from werkzeug.utils import secure_filename
from blaze import resource

logger = logging.getLogger(__name__)

class DataManager(object):
    def __init__(self, settings):
        self.settings = settings
        self._storage_time = 0
        self._all_datasets = None

    def write(self, username, filename, fileobj):
        path = self.data_path(username, filename, absolute=True)
        if not exists(dirname(path)):
            os.makedirs(dirname(path))
        with open(path, "wb+") as f:
            f.write(path)

    def ls(self, username=None):
        if username:
            users = [username]
        else:
            users = os.listdir(self.settings.data_directory)
        files = []
        for u in users:
            for fname in  os.listdir(self.data_path(u, "", absolute=True)):
                files.append(join(u, fname))
        return files

    def parse(self, uri):
        protocol = datapath = None
        if '://' in uri:
            protocol, uri = uri.split('://')
        if '::' in uri:
            uri, datapath = uri.split('::')
        username = dirname(uri)
        fpath = relpath(uri, username)
        return protocol, username, fpath, datapath

    def data_path(self, username, filename, absolute=False):
        # TODO - invalid usernames makes these paths un-parseable
        # we should probably restrict invalid usernames
        username = secure_filename(username)
        filename = secure_filename(filename)
        if absolute:
            return join(self.settings.data_directory, username, filename)
        else:
            return join(username, filename)

    def configure(self, username, filename, **kwargs):
        relpath = self.data_path(username, filename, absolute=False)
        self.settings.storage['_update_time'] = time.time()
        self.settings.storage[relpath] = kwargs
        self.settings.storage.sync()

    def all_datasets(self):
        storage = self.settings.storage
        last_storage_time = self._storage_time
        last_change = storage.get('_update_time', 0)
        result = {}
        if self._all_datasets is None or last_storage_time < last_change:
            result = copy.copy(self.settings.data)
            for k,v in self.settings.data.items():
                result[k] = v
            for k,v in storage.items():
                if k == '_update_time':
                    continue
                try:
                    result[k] = resource(join(self.settings.data_directory, k), **v)
                except Exception as e:
                    import pdb;pdb.set_trace()
                    logger.exception(e)
            self._all_datasets = result
            self._storage_time = last_change
        return self._all_datasets
