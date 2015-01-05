import json

from flask import request
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
