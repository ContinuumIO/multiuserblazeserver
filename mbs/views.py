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

def data_path(username, filename):
    filename = secure_filename(filename)
    username_path = secure_filename(username)
    path = join(settings.data_directory, username_path, filename)
    return path

@mbsbp.route("/upload", methods=['POST'])
def upload():
    username = settings.auth_backend.current_username()
    f = request.files['file']
    path = data_path(username, f.filename)
    if not settings.auth_backend.can_write(path, username):
        return abort(403)
    if not exists (dirname(path)):
        os.makedirs(dirname(path))
    f.save(path)
    return jsonify(path=relpath(path, settings.data_directory))
