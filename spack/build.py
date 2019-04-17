"""
Build cvmfs versions >=v4 with spack.
Or IceProd versions >=v2.5.0.
"""
from __future__ import print_function

import sys
import os
import shutil
import tempfile
import subprocess
from collections import OrderedDict

def myprint(*args,**kwargs):
    """Flush the print immediately, so it syncs with subprocess stdout"""
    print(*args,**kwargs)
    sys.stdout.flush()

def run_cmd(*args, **kwargs):
    """print and run a subprocess command"""
    myprint('cmd:',*args)
    subprocess.check_call(*args, **kwargs)

def run_cmd_output(*args, **kwargs):
    """print and run a subprocess command, with output"""
    myprint('cmd:',*args)
    p = subprocess.Popen(*args,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         **kwargs)
    output,error = p.communicate()
    return (p.returncode, output.decode('utf-8'), error.decode('utf-8'))

def get_sroot(dir_name):
    """Get the SROOT from dir/setup.sh"""
    code,output,error = run_cmd_output(os.path.join(dir_name,'setup.sh'), shell=True)
    for line in output.split(';'):
        line = line.strip()
        myprint(line)
        if line and line.startswith('export'):
            parts = line.split('=',1)
            name = parts[0].replace('export ','').strip()
            value = parts[1].strip(' "')
            if name in ('SROOT','ICEPRODROOT'):
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

def disable_compiler(spack_path, compiler):
    """
    Disable the compiler config for spack.

    Args:
        spack_path (str): path to spack
        compiler (str): name of compiler package
    """
    myprint('disable_compiler',compiler)
    spack_bin = os.path.join(spack_path,'bin','spack')

    # get arch
    code,output,error = run_cmd_output([spack_bin, 'arch'])
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
    myprint('update_compiler',compiler)
    spack_bin = os.path.join(spack_path,'bin','spack')

    # get arch
    code,output,error = run_cmd_output([spack_bin, 'arch'])
    spack_arch = output.strip(' \n')
    platform = spack_arch.split('-')[1]

    # get compiler
    code,output,error = run_cmd_output([spack_bin, 'location', '-i', compiler])
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
    ret = OrderedDict()
    with open(filename) as f:
        for line in f.read().split('\n'):
            line = line.strip()
            if (not line) or line.startswith('#'):
                continue
            name = line.split('@',1)[0]
            ret[name] = line
    return ret

def get_dependencies(spack_path, package, packages):
    """
    Get the correct versions for all dependencies.

    If we have the package in our list, pin to that version.
    Otherwise, let spack pick.

    Args:
        spack_path (str): path to spack
        package (str): the package to check
        packages (dict): all installed packages
    Returns:
        list: [dependencies]
    """
    spack_bin = os.path.join(spack_path,'bin','spack')
    cmd = [spack_bin, 'find', '--show-full-compiler', '-v']
    code,output,error = run_cmd_output(cmd)
    installed_packages = {}
    for line in output.split('\n'):
        line = line.strip()
        if (not line) or line.startswith('--') or line.startswith('==>'):
            continue
        parts = line.split()
        # test for our compiler
        if 'spack' not in parts[0].split('%',1)[-1]:
            continue
        name = parts[0].split('@',1)[0]
        parts2 = [x for x in parts if not x.endswith('=')]
        installed_packages[name] = ' '.join(parts2)

    dependencies = set()
    ret = []
    success = False
    while True:
        cmd = [spack_bin, 'spec']+package.split()+ret
        code,output,error = run_cmd_output(cmd)
        success = code == 0

        if (not success) and 'while trying to concretize' in error:
            output = error.split('while trying to concretize',1)[-1]
            success = True
        if success:
            new_deps = set()
            for line in output.split('\n'):
                line = line.strip()
                if line.startswith('^'):
                    dep = line.split('@', 1)[0].lstrip('^')
                    print('dep:',dep)
                    if dep in packages:
                        print('   found', packages[dep])
                        new_deps.add(dep)
                    elif dep in installed_packages:
                        print('   installed', installed_packages[dep])
                        new_deps.add(dep)
            if new_deps == dependencies:
                break
            dependencies = new_deps
        else:
            for line in error.split('\n'):
                if line.startswith('==> Error:'):
                    for d in line.split('depend on')[-1].replace(', or ',',').replace(' or ',',').split(','):
                        d = d.strip()
                        if d in dependencies:
                            dependencies.remove(d)
                        else:
                            print(line)
                            raise Exception('bad dependencies')
                    break
            else:
                print(output)
                print(error)
                raise Exception('bad dependencies')

        ret = []
        for d in dependencies:
            if d in packages:
                parts = packages[d].split()
            elif d in installed_packages:
                parts = installed_packages[d].split()
            else:
                raise Exception('bad dep: '+d)
            parts[0] = '^'+parts[0]
            ret.extend(parts)
    
    return ret

def is_installed(spack_path, package):
    """Check if a package is installed"""
    spack_bin = os.path.join(spack_path,'bin','spack')
    cmd = [spack_bin, 'find', package]
    code,output,error = run_cmd_output(cmd)
    name = package.split('@')[0]
    for line in output.split('\n'):
        line = line.strip()
        if (not line) or line.startswith('--') or line.startswith('==>'):
            continue
        if name in line:
            return True
    return False

def uninstall(spack_path, sroot, package):
    """Uninstall package and remove from view"""
    spack_bin = os.path.join(spack_path, 'bin', 'spack')
    cmd = [spack_bin, 'view', '-v', '-d', 'false', 'rm',
           '--no-remove-dependents', sroot, package]
    run_cmd(cmd)
    cmd = [spack_bin, 'uninstall', '-y', '-f', '-a', package]
    run_cmd(cmd)

def build(src, dest, version):
    myprint('building version',version)
    if 'PYTHONPATH' in os.environ:
        del os.environ['PYTHONPATH']

    version = version.split('/') if '/' in version else [version]

    srootbase = os.path.join(dest,*version)
    if version[0] == 'iceprod':
        copy_src(os.path.join(src,'iceprod','all'), srootbase)
    elif '.' in version[0] and not os.path.exists(os.path.join(src,*version)):
        copy_src(os.path.join(src,version[0].split('.')[0],*version[1:]), srootbase)
    else:
        copy_src(os.path.join(src,*version), srootbase)
    sroot = get_sroot(srootbase)
    #if version == ['iceprod','master']:
    #    myprint('iceprod/master - deleting sroot')
    #    shutil.rmtree(sroot)
    if not os.path.isdir(sroot):
        os.makedirs(sroot)

    # make I3_DATA symlinks
    i3_data = os.path.join(dest,'data')
    for path in ('etc/vomsdir','etc/vomses','share/certificates',
                 'share/vomsdir'):
        basedir = os.path.join(sroot,os.path.dirname(path))
        if not os.path.isdir(basedir):
            os.makedirs(basedir)
        if not os.path.lexists(os.path.join(sroot,path)):
            os.symlink(os.path.join(i3_data,'voms',path),
                       os.path.join(sroot,path))

    # set up spack
    spack_path = os.path.join(sroot, 'spack')
    if not os.path.exists(spack_path):
        url = 'https://github.com/spack/spack.git'
        run_cmd(['git', 'clone', url, spack_path])
        run_cmd(['git', 'checkout', 'tags/v0.12.0'], cwd=spack_path)
        
    os.environ['SPACK_ROOT'] = spack_path
    spack_bin = os.path.join(spack_path,'bin','spack')

    try:
        run_cmd([spack_bin, 'repo', 'add', '--scope', 'site',
                 os.path.join(os.path.dirname(__file__),'repo')])
    except Exception:
        pass

    hep_repo_path = os.path.join(spack_path,'spack/var/spack/repos/hep-spack')
    if not os.path.exists(spack_path):
        url = 'https://github.com/HEP-SF/hep-spack.git'
        run_cmd(['git', 'clone', url, hep_repo_path])
        run_cmd([spack_bin, 'repo', 'add', '--scope', 'site',
                 hep_repo_path])

    try:
        # setup compiler
        compiler_package = ''
        path = os.path.join(os.path.dirname(__file__), *version)+'-compiler'
        if os.path.exists(path):
            packages = get_packages(path)
            for name, package in packages.items():
                if 'gcc' in name or 'llvm' in name:
                    compiler_package = package.split()[0]
            if not compiler_package:
                raise Exception('could not find compiler package name')
            disable_compiler(spack_path, compiler_package)

            cmd = [spack_bin, 'install', '-y', '-v']
            if 'CPUS' in os.environ:
                cmd.extend(['-j', os.environ['CPUS']])
            for name, package in packages.items():
                myprint('installing', name)
                run_cmd(cmd+package.split())
            update_compiler(spack_path, compiler_package)
        
        # install packages
        packages = get_packages(os.path.join(os.path.dirname(__file__), *version))
        cmd = [spack_bin, 'install', '-y', '-v', '--no-checksum']
        if 'CPUS' in os.environ:
            cmd.extend(['-j', os.environ['CPUS']])
        for name, package in packages.items():
            myprint('installing', name)
            main_pkg = package.split()[0]
            installed = is_installed(spack_path, main_pkg)
            if '@develop' in main_pkg and installed:
                uninstall(spack_path, sroot, main_pkg)
            elif installed:
                myprint(name, 'already installed')
                continue
            deps = get_dependencies(spack_path, package, packages)
            run_cmd(cmd+package.split()+deps)

        # set up view
        if compiler_package:
            run_cmd([spack_bin, 'view', '-d', 'false', 'soft', '-i', sroot, compiler_package])
            if not os.path.exists(os.path.join(sroot,'bin','cc')):
                run_cmd(['ln','-s','gcc','cc'], cwd=os.path.join(sroot,'bin'))
        cmd = [spack_bin, 'view', 'soft', '-i', sroot]
        for name, package in packages.items():
            myprint('adding', name, 'to view')
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
