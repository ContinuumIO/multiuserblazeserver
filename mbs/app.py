import argparse

from flask import Flask, Blueprint

from .settings import settings

mbsbp = Blueprint('mbs', 'mbs')

def setup_app(config_file=None):
    app = Flask('mbs')
    if config_file is not None:
        settings.from_pyfile(config_file)
    settings.postprocess()
    from . import views
    app.register_blueprint(mbsbp)
    return app

def run(config_file=None):
    app = setup_app(config_file=config_file)
    app.debug = True
    app.run(host=settings.ip, port=settings.port)
