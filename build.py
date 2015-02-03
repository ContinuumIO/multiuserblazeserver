import os
from os.path import join, getctime, dirname
import glob
import subprocess
import argparse

def newest_file(root):
    path = join(root, "*tar.bz2")
    newest = max(glob.iglob(path), key=getctime)
    return newest

def upload(pkg, user):
    cmd = ["binstar", "upload", "--force","-u", user, pkg]
    subprocess.check_call(cmd)

def build(recipe, build_path, pythons=[], platforms=[], binstar_user=None):
    print (recipe, pythons, platforms)
    for p in pythons:
        cmd = ["conda", "build", recipe, "--python", p]
        subprocess.check_call(cmd)
        pkg = newest_file(build_path)
        if binstar_user:
            upload(pkg, binstar_user)
        for plat in platforms:
            cmd = ["conda", "convert", "-p", plat, pkg]
            subprocess.check_call(cmd)
            if binstar_user:
                to_upload = newest_file(plat)
                upload(to_upload, binstar_user)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("build_dir")
    p.add_argument("--py", action="append", default=[])
    p.add_argument("--plat", action="append", default=[])
    p.add_argument("-u", "--binstar-user", help="binstar user")
    args = p.parse_args()
    build_dir = p.add_argument("build_dir")

    build("conda.recipe", args.build_dir, args.py, args.plat, args.binstar_user)
    #build("../into/conda.recipe", args.build_dir, args.py, args.plat, args.binstar_user)
    """
    python build.py /opt/anaconda/conda-bld/linux-64 --py 27 --py 34 --plat osx-64 --plat win-64 -u hugo
    """
