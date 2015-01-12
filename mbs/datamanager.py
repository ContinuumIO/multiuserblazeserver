from os.path import join, dirname, exists, relpath, isdir
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
            dirpath = self.data_path(u, "", absolute=True)
            if not isdir(dirpath):
                continue
            for fname in os.listdir(dirpath):
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

    def configure(self, uri, **kwargs):
        self.settings.storage['_update_time'] = time.time()
        self.settings.storage[uri] = kwargs
        self.settings.storage.sync()

    def delete(self, uri):
        self.settings.storage['_update_time'] = time.time()
        self.settings.storage.pop(uri, None)
        self.settings.storage.sync()

    def resolve_resource(self, uri):
        """parses a resource (where the file base resources are stored
        as a relative path to the data directory and resolves it
        """
        protocol, username, fpath, datapath = self.parse(uri)
        if protocol and protocol != 'hdfstore':
            raise NotImplementedError
        path = self.data_path(username, fpath, absolute=True)
        if protocol:
            protocol = protocol + "://"
        else:
            protocol = ""
        if datapath:
            datapath = "::" + datapath
        else:
            datapath = ""
        return protocol + path + datapath

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
                    result[k] = resource(self.resolve_resource(k), **v)
                except Exception as e:
                    logger.exception(e)
                    raise
            self._all_datasets = result
            self._storage_time = last_change
        return self._all_datasets
