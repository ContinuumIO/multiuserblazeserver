from os.path import dirname, join

def config_file(name):
    return join(dirname(__file__), 'config', name)
