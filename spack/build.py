"""
Build cvmfs versions >=v4 with spack.
"""
from __future__ import print_function

import os
import shutil
import tempfile
import subprocess

def get_sroot(dir_name):
    """Get the SROOT from dir/setup.sh"""
    p = subprocess.Popen(os.path.join(dir_name,'setup.sh'),
                         shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    output = p.communicate()[0]
    for line in output.split(';'):
        line = line.strip()
        print(line)
        if line and line.startswith('export'):
            parts = line.split('=',1)
            name = parts[0].replace('export ','').strip()
            value = parts[1].strip(' "')
            if name == 'SROOT':
                return value
    raise Exception('could not find SROOT')

def copy_src(src,dest):
    """Copy anything from src to dest"""
    try:
        os.makedirs(dest)
    except Exception:
        pass
    for p in os.listdir(src):
        if p.startswith('.'):
            continue
        path = os.path.join(src,p)
        if os.path.isdir(path):
            copy_src(path,os.path.join(dest,p))
        else:
            shutil.copy2(path,dest)

def run_cmd(*args, **kwargs):
    """print and run a subprocess command"""
    print('cmd:',*args)
    subprocess.check_call(*args, **kwargs)

def get_packages(filename):
    """
    Get packages from a file.

    Args:
        filename (str): the filename to read from
    Returns:
        dict: {package name: install string}
    """
    ret = {}
    with open(filename) as f:
        for line in f.read().split('\n'):
            line = line.strip()
            if line.startswith('#'):
                continue
            name = line.split('@',1)[0]
            ret[name] = line
    return ret

def build(src, dest, version):
    print('building version',version)

    # set up spack
    spack_path = os.path.join(dest, 'spack')
    if not os.path.exists(spack_path):
        url = 'https://github.com/spack/spack.git'
        run_cmd(['git', 'clone', url, spack_path])
    #copy_src(os.path.join(os.path.dirname(__file__),'etc'),
    #         os.path.join(spack_path,'etc'))
        
    os.environ['SPACK_ROOT'] = spack_path
    spack_bin = os.path.join(spack_path,'bin','spack')
    try:
        run_cmd([spack_bin, 'repo', 'add',
                 os.path.join(os.path.dirname(__file__),'repo')])
    except Exception:
        pass

    try:
        # install packages
        packages = get_packages(os.path.join(os.path.dirname(__file__), version))

        cmd = [spack_bin, 'install', '-y']
        if 'CPUS' in os.environ:
            cmd.extend(['-j', os.environ['CPUS']])
        for p in packages:
            print('installing',p)
            run_cmd(cmd+packages[p].split())

        # set up view
        copy_src(os.path.join(src,version), os.path.join(dest,version))
        sroot = get_sroot(os.path.join(dest,version))
        cmd = [spack_bin, 'view', 'soft', '-i', sroot]
        for p in packages:
            print('adding',p,'to view')
            run_cmd(cmd+packages[p].split()[:1])

    finally:
        # cleanup
        run_cmd([spack_bin,'clean','-s','-d'])

if __name__ == '__main__':
    from optparse import OptionParser

    parser = OptionParser(usage="%prog [options] versions")
    parser.add_option("--src", help="base source path")
    parser.add_option("--dest", help="base dest path")
    (options, args) = parser.parse_args()
    if not args:
        parser.error("need to specify a version")

    for version in args:
        build(options.src, options.dest, version)
