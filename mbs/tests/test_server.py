from __future__ import absolute_import, division, print_function
from os.path import dirname, join as pjoin
from datetime import datetime

from nose.tools import with_setup
import datashape
import numpy as np
from flask import json
from datetime import datetime
from pandas import DataFrame
from toolz import pipe

from blaze.utils import example
from blaze import discover, symbol, by, CSV, compute, join, into
from blaze.server.server import to_tree, from_tree

from mbs.app import setup_app
from mbs.settings import settings
from . import config_file
test = None
data = None
t = None

def setup_function():
    global app
    global test
    global data
    global t

    config = config_file("config.py")
    app = setup_app(config_file=config)
    test = app.test_client()
    data = settings.data
    t = symbol('t', discover(data))

def teardown_function():
    global app
    global test
    global data

    app = None
    test = None
    data = None

@with_setup(setup_function, teardown_function)
def test_datasets():
    response = test.get('/datashape')
    assert response.data.decode('utf-8') == str(discover(data))

@with_setup(setup_function, teardown_function)
def test_bad_responses():
    assert 'OK' not in test.post('/compute/accounts.json',
                                 data = json.dumps(500),
                                 content_type='application/json').status
    assert 'OK' not in test.post('/compute/non-existent-table.json',
                                 data = json.dumps(0),
                                 content_type='application/json').status
    assert 'OK' not in test.post('/compute/accounts.json').status


@with_setup(setup_function, teardown_function)
def test_compute():
    expr = t.accounts.amount.sum()
    query = {'expr': to_tree(expr)}
    expected = 300

    response = test.post('/compute.json',
                         data = json.dumps(query),
                         content_type='application/json')

    assert 'OK' in response.status
    assert json.loads(response.data.decode('utf-8'))['data'] == expected

@with_setup(setup_function, teardown_function)
def test_get_datetimes():
    events = data['events']
    expr = t.events
    query = {'expr': to_tree(expr)}

    response = test.post('/compute.json',
                         data=json.dumps(query),
                         content_type='application/json')

    assert 'OK' in response.status
    result = json.loads(response.data.decode('utf-8'))
    ds = datashape.dshape(result['datashape'])
    result = into(np.ndarray, result['data'], dshape=ds)
    assert into(list, result) == into(list, events)

@with_setup(setup_function, teardown_function)
def test_multi_expression_compute():
    s = symbol('s', discover(data))

    expr = join(s.accounts, s.cities)

    resp = test.post('/compute.json',
                     data=json.dumps({'expr': to_tree(expr)}),
                     content_type='application/json')

    assert 'OK' in resp.status
    result = json.loads(resp.data.decode('utf-8'))['data']
    expected = compute(expr, {s: data})

    assert list(map(tuple, result))== into(list, expected)

@with_setup(setup_function, teardown_function)
def test_leaf_symbol():
    cities = data['cities']
    query = {'expr': {'op': 'Field', 'args': [':leaf', 'cities']}}
    resp = test.post('/compute.json',
                     data=json.dumps(query),
                     content_type='application/json')

    a = json.loads(resp.data.decode('utf-8'))['data']
    b = into(list, cities)

    assert list(map(tuple, a)) == b
