from os.path import dirname, join

def config_file(name):
    return join(dirname(__file__), 'config', name)

def data_file(name):
    return join(dirname(__file__), 'data', name)
