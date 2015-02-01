import json
from os.path import join, dirname, exists, relpath
import os
import traceback
import logging

from werkzeug.utils import secure_filename
from flask import request, abort, jsonify
from datashape import Mono, discover
from datashape.predicates import iscollection
from blaze.utils import json_dumps
from blaze.server.server import to_tree, from_tree
from blaze import into, compute
from blaze.expr import Expr, Symbol, Selection, Broadcast, symbol
from blaze.expr.parser import exprify

from .app import mbsbp
from .settings import settings
from .errors import ServerException

logger = logging.getLogger(__name__)

@mbsbp.route('/datashape')
def dataset():
    return str(discover(settings.datamanager.all_datasets()))


@mbsbp.app_errorhandler(ServerException)
def error(e):
    response = jsonify(e.to_dict())
    response.status_code = e.status_code
    return response

def _compserver(payload):
    dataset = settings.datamanager.all_datasets()
    ns = payload.get('namespace', dict())

    ns[':leaf'] = symbol('leaf', discover(dataset))

    expr = from_tree(payload['expr'], namespace=ns)
    assert len(expr._leaves()) == 1
    leaf = expr._leaves()[0]

    try:
        result = compute(expr, {leaf: dataset})
    except Exception as e:
        logger.exception(e)
        msg = traceback.format_exc()
        raise ServerException(msg, status_code=500)
    return expr, result

@mbsbp.route('/compute.json', methods=['POST', 'PUT', 'GET'])
#TODO add read-only authentication checks by parsing the expr graph
def compserver():
    if not request.json:
        raise ServerException('Expected JSON data', status_code=404)
    payload = request.json
    expr, result = _compserver(payload)
    if iscollection(expr.dshape):
        result = into(list, result)
    return json.dumps({'datashape': str(expr.dshape),
                       'names' : expr.fields,
                       'data': result}, default=json_dumps)

@mbsbp.route("/upload", methods=['POST'])
def upload():
    username = settings.auth_backend.current_username()
    f = request.files['file']
    path = settings.datamanager.data_path(username, f.filename, absolute=True)
    if not settings.auth_backend.can_write(path, username):
        return abort(403)
    if not exists (dirname(path)):
        os.makedirs(dirname(path))
    f.save(path)
    path = settings.datamanager.data_path(username, f.filename, absolute=False)
    return jsonify(path=path)

@mbsbp.route("/ls/<username>", methods=['GET'])
@mbsbp.route("/ls", methods=['GET'])
def ls(username=None):
    return jsonify(files=settings.datamanager.ls(username=username))

@mbsbp.route("/configure", methods=['POST'])
def configure():
    kwargs = request.json['kwargs']
    uri = request.json['uri']
    delete = request.json.get('_delete', False)
    username = settings.auth_backend.current_username()
    protocol, fusername, fpath, datapath = settings.datamanager.parse(uri)
    complete_path = settings.datamanager.data_path(fusername, fpath)
    if not settings.auth_backend.can_write(complete_path, username):
        return abort(403)
    if delete:
        settings.datamanager.delete(uri.encode('utf-8'))
    else:
        settings.datamanager.configure(uri.encode('utf-8'), **kwargs)
    return jsonify(status='success')
