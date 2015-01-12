import json
from os.path import join, dirname, exists, relpath
import os

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

@mbsbp.route('/datashape')
def dataset():
    return str(discover(settings.data))

@mbsbp.route('/compute.json', methods=['POST', 'PUT', 'GET'])
#TODO add read-only authentication checks by parsing the expr graph
def compserver():
    dataset = settings.data
    if request.headers['content-type'] != 'application/json':
        return ("Expected JSON data", 404)
    try:
        payload = json.loads(request.data.decode('utf-8'))
    except ValueError:
        return ("Bad JSON.  Got %s " % request.data, 404)

    ns = payload.get('namespace', dict())
    ns[':leaf'] = symbol('leaf', discover(dataset))

    expr = from_tree(payload['expr'], namespace=ns)
    assert len(expr._leaves()) == 1
    leaf = expr._leaves()[0]

    try:
        result = compute(expr, {leaf: dataset})
    except Exception as e:
        return ("Computation failed with message:\n%s" % e, 500)

    if iscollection(expr.dshape):
        result = into(list, result)

    return json.dumps({'datashape': str(expr.dshape),
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
def ls(username=None):
    return jsonify(files=settings.datamanager.ls(username=username))

@mbsbp.route("/configure", methods=['POST'])
def configure():
    kwargs = request.json['kwargs']
    uri = request.json['uri']
    username = settings.auth_backend.current_username()
    protocol, fusername, fpath, datapath = settings.datamanager.parse(uri)
    complete_path = settings.datamanager.data_path(fusername, fpath)
    if not settings.auth_backend.can_write(complete_path, username):
        return abort(403)
    settings.datamanager.configure(fusername, fpath, **kwargs)
    return jsonify(status='success')
