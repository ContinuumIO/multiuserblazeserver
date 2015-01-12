import argparse

from mbs.app import run

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument('config_file', default=None, nargs="?")
    args = p.parse_args()
    run(config_file=args.config_file)
