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

def disable_compiler(spack_path, compiler):
    """
    Disable the compiler config for spack.

    Args:
        spack_path (str): path to spack
        compiler (str): name of compiler package
    """
    print('disable_compiler',compiler)
    spack_bin = os.path.join(spack_path,'bin','spack')

    # get arch
    p = subprocess.Popen([spack_bin, 'arch'],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    output = p.communicate()[0]
    spack_arch = output.strip(' \n')
    platform = spack_arch.split('-')[1]

    # update compilers.yaml
    compiler_cfg = os.path.join(spack_path,'etc','spack','compilers.yaml')
    if os.path.exists(compiler_cfg):
        with open(compiler_cfg) as f:
            compiler_txt = f.read()
        compiler_lines = compiler_txt.split('\n')
        start_line = -1
        output_lines = []
        for i,line in enumerate(compiler_lines):
            if line == '- compiler:':
                if start_line > 0:
                    output_lines.extend(compiler_lines[start_line:i])
                start_line = i
            elif 'operating_system: {}'.format(platform) in line:
                start_line = -1 # erase this compiler
        if start_line > 0:
            output_lines.extend(compiler_lines[start_line:])

        if output_lines:
            with open(compiler_cfg, 'w') as f:
                f.write('compilers:\n')
                for line in output_lines:
                    f.write(line+'\n')
        else:
            os.remove(compiler_cfg)

    # update packages.yaml
    packages_cfg = os.path.join(spack_path,'etc','spack','packages.yaml')
    if os.path.exists(packages_cfg):
        with open(packages_cfg) as f:
            packages_txt = f.read()
    else:
        packages_txt = 'packages:\n  all:'
    with open(packages_cfg,'w') as f:
        for line in packages_txt.split('\n'):
            if 'compiler:' in line:
                continue
            f.write(line+'\n')

def update_compiler(spack_path, compiler):
    """
    Update the compiler config for spack.

    Args:
        spack_path (str): path to spack
        compiler (str): name of compiler package
    """
    print('update_compiler',compiler)
    spack_bin = os.path.join(spack_path,'bin','spack')

    # get arch
    p = subprocess.Popen([spack_bin, 'arch'],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    output = p.communicate()[0]
    spack_arch = output.strip(' \n')
    platform = spack_arch.split('-')[1]

    # get compiler
    p = subprocess.Popen([spack_bin, 'location', '-i', compiler],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    output = p.communicate()[0]
    loc = output.strip(' \n')
    if (not loc) or not os.path.exists(loc):
        raise Exception('cannot find compiler '+compiler)

    # update compilers.yaml
    compiler_cfg = os.path.join(spack_path,'etc','spack','compilers.yaml')
    if os.path.exists(compiler_cfg):
        with open(compiler_cfg) as f:
            compiler_txt = f.read()
    else:
        compiler_txt = 'compilers:\n'
    compiler_txt += """
- compiler:
    modules: []
    operating_system: {0}
    paths:
      cc: {1}/bin/gcc
      cxx: {1}/bin/g++
      f77: {1}/bin/gfortran
      fc: {1}/bin/gfortran
    spec: {2}spack""".format(platform, loc, compiler)
    with open(compiler_cfg, 'w') as f:
        f.write(compiler_txt)

    # update packages.yaml
    packages_cfg = os.path.join(spack_path,'etc','spack','packages.yaml')
    if os.path.exists(packages_cfg):
        with open(packages_cfg) as f:
            packages_txt = f.read()
    else:
        packages_txt = 'packages:\n  all:\n'
    if 'compiler' not in packages_txt:
        packages_txt = packages_txt.replace('all:','all:\n    compiler: [{}spack]'.format(compiler))
        with open(packages_cfg,'w') as f:
            f.write(packages_txt)

def get_packages(filename):
    """
    Get packages from a file.

    Args:
        filename (str): the filename to read from
    Returns:
        list: [(package name, install string)]
    """
    ret = []
    with open(filename) as f:
        for line in f.read().split('\n'):
            line = line.strip()
            if (not line) or line.startswith('#'):
                continue
            name = line.split('@',1)[0]
            ret.append((name, line))
    return ret

def build(src, dest, version):
    print('building version',version)
    del os.environ['PYTHONPATH']

    # set up spack
    spack_path = os.path.join(dest, 'spack')
    if not os.path.exists(spack_path):
        url = 'https://github.com/spack/spack.git'
        run_cmd(['git', 'clone', url, spack_path])
        
    os.environ['SPACK_ROOT'] = spack_path
    spack_bin = os.path.join(spack_path,'bin','spack')
    try:
        run_cmd([spack_bin, 'repo', 'add', '--scope', 'site',
                 os.path.join(os.path.dirname(__file__),'repo')])
    except Exception:
        pass

    try:
        # setup compiler
        compiler_package = ''
        path = os.path.join(os.path.dirname(__file__), version+'-compiler')
        if os.path.exists(path):
            packages = get_packages(path)
            for name, package in packages:
                if 'gcc' in name:
                    compiler_package = package.split()[0]
            if not compiler_package:
                raise Exception('could not find compiler package name')
            disable_compiler(spack_path, compiler_package)

            cmd = [spack_bin, 'install', '-y']
            if 'CPUS' in os.environ:
                cmd.extend(['-j', os.environ['CPUS']])
            for name, package in packages:
                print('installing', name)
                run_cmd(cmd+package.split())
            update_compiler(spack_path, compiler_package)
        
        # install packages
        packages = get_packages(os.path.join(os.path.dirname(__file__), version))

        cmd = [spack_bin, 'install', '-y']
        cmd_activate = [spack_bin, 'activate']
        if 'CPUS' in os.environ:
            cmd.extend(['-j', os.environ['CPUS']])
        for name, package in packages:
            print('installing', name)
            run_cmd(cmd+package.split())
            if name.startswith('py-'):
                run_cmd(cmd_activate+[name])

        # set up view
        copy_src(os.path.join(src,version), os.path.join(dest,version))
        sroot = get_sroot(os.path.join(dest,version))
        run_cmd([spack_bin, 'view', '-d', 'false', 'soft', '-i', sroot, compiler_package])
        cmd = [spack_bin, 'view', 'soft', '-i', sroot]
        for name, package in packages:
            print('adding', name, 'to view')
            view_cmd = cmd+package.split()[:1]
            if compiler_package:
                view_cmd[-1] += '%'+compiler_package+'spack'
            run_cmd(view_cmd)

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
