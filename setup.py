# needs to be tested
from __future__ import print_function
import sys
if len(sys.argv)>1 and sys.argv[1] == 'develop':
    # Only import setuptools if we have to
    import site
    from os.path import dirname, abspath, join
    site_packages = site.getsitepackages()[0]
    fname = join(site_packages, "mbs.pth")
    path = abspath(dirname(__file__))
    with open(fname, "w+") as f:
        f.write(path)
    print("develop mode, wrote path (%s) to (%s)" % (path, fname))
    sys.exit()

from distutils.core import setup
try:
    import setuptools
except:
    pass
import os
import sys
__version__ = (0, 2, 1)
setup(
    name = 'multiuserblazeserver',
    version = '.'.join([str(x) for x in __version__]),
    install_requires=['blaze >= 0.7.2', 'into >= 0.2.1'],
    packages = ['mbs',
                'mbs.scripts',
                'mbs.tests',
                ],
    url = 'http://github.com/ContinuumIO/multiuserblazeserver',
    description = 'Multi User Blaze Server',
    zip_safe=False,
    author='Continuum Analytics',
    author_email='',
    license = 'New BSD',
)
