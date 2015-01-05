import os
import imp
import uuid
import copy

defaults = dict(
    data_directory=os.getcwd(),
    data={},
    multi_user=False,
    ip="0.0.0.0",
    port=6039,
    url_prefix="",
)

class Settings(object):
    bp_settings = ['data_directory', 'data', 'multi_user']
    app_settings = ['ip', 'port', 'url_prefix']

    def reset(self):
        for k,v in defaults.iteritems():
            setattr(self, k, copy.copy(v))

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

settings = Settings()
settings.reset()
del Settings
