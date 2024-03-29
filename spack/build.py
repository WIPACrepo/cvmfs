"""
Build cvmfs versions >=v4 with spack.
Or IceProd versions >=v2.5.0.
"""
from __future__ import print_function

import sys
import os
import shutil
import tempfile
import time
import subprocess
import atexit
import signal
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

def run_cmd_sroot(args, srootbase, **kwargs):
    """print and run a subprocess command, inside an sroot environment."""
    myprint('cmd:',args)
    cmd = 'eval $('+os.path.join(srootbase,'setup.sh')+') ; '
    cmd += ' '.join(args)
    subprocess.check_call(cmd, shell=True, **kwargs)

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
    print("copy_src")
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
    cmd = [spack_bin, 'find', '--show-full-compiler', '-lv']
    code,output,error = run_cmd_output(cmd)
    installed_packages = {}
    for line in output.split('\n'):
        line = line.strip()
        if (not line) or line.startswith('--') or line.startswith('==>'):
            continue
        parts = line.split()
        # test for our compiler
        if 'spack' not in parts[1].split('%',1)[-1]:
            continue
        name = parts[1].split('@',1)[0]
        hash = parts[0]
        installed_packages[name] = name+'/'+hash

    dependencies = set()
    ret = []
    success = False
    for _ in range(50):
        cmd = [spack_bin, 'spec']+package.split()+ret
        code,output,error = run_cmd_output(cmd)
        success = code == 0

        if (not success) and 'while trying to concretize the partial spec:' in error:
            for line in error.rsplit('partial spec:',1)[-1].split('\n'):
                line = line.strip()
                if line and '@' in line:
                    dep = line.split('@', 1)[0]
                    if dep in packages:
                        print('   found', packages[dep])
                        dependencies.add(dep)
                        break
                    elif dep in installed_packages:
                        print('   installed', installed_packages[dep])
                        dependencies.add(dep)
                        break
            else:
                print(output)
                print(error)
                raise Exception('bad dependencies')
        else:
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
            if d in installed_packages:
                parts = installed_packages[d].split()
            elif d in packages:
                parts = packages[d].split()
            else:
                raise Exception('bad dep: '+d)
            parts[0] = '^'+parts[0]
            ret.extend(parts)
    else:
        print(output)
        print(error)
        raise Exception('bad dependencies')

    return ret

def is_installed(spack_path, package):
    """Check if a package is installed"""
    name = package.split('@')[0]
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
        pkg_name = parts[0].split('@',1)[0]
        if name == pkg_name:
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

class Mirror:
    def __init__(self, mirror_path):
        self.mirror_path = mirror_path
        self.spack_bin = None
        if mirror_path and mirror_path.startswith('/'):
            # set up spack latest version for mirror
            spack_path = os.path.join(os.getcwd(), 'spack')
            if not os.path.exists(spack_path):
                url = 'https://github.com/spack/spack.git'
                run_cmd(['git', 'clone', url, spack_path])
            self.spack_bin = os.path.join(spack_path, 'bin', 'spack')

    def add_repo(self, repo_path):
        if self.spack_bin:
            try:
                run_cmd([self.spack_bin, 'repo', 'add', '--scope', 'site', repo_path])
            except:
                pass

    def download(self, package):
        if self.spack_bin:
            pkg_version = package.split()[0]
            pkg_name = pkg_version.split('@')[0]
            pkg_version_name = pkg_version.replace('@','-')+'.tar.gz'
            if os.path.exists(os.path.join(self.mirror_path, pkg_name, pkg_version_name)):
                myprint(pkg_version+' already in mirror')
                return
            pkg_version_name = pkg_version.replace('@','-')+'.tar.bz2'
            if os.path.exists(os.path.join(self.mirror_path, pkg_name, pkg_version_name)):
                myprint(pkg_version+' already in mirror')
                return
            pkg_version_name = pkg_version.replace('@','-')+'.tar.xz'
            if os.path.exists(os.path.join(self.mirror_path, pkg_name, pkg_version_name)):
                myprint(pkg_version+' already in mirror')
                return
            myprint('attempting to add '+pkg_version+' to mirror')
            try:
                run_cmd([self.spack_bin, 'mirror', 'create', '-d', self.mirror_path, pkg_version])
            except Exception:
                pass

def build(src, dest, version, mirror=None):
    myprint('building version',version)
    if 'PYTHONPATH' in os.environ:
        del os.environ['PYTHONPATH']

    version = version.split('/') if '/' in version else [version]

    srootbase = os.path.join(dest,*version)
    try:
        sroot = get_sroot(srootbase)
    except Exception:
        sroot = None
    if (not sroot) or sroot == 'RHEL_7_x86_64' or not sroot.startswith('/cvmfs'):
        if version[0] == 'iceprod':
            copy_src(os.path.join(src,'iceprod','all'), srootbase)
        elif '.' in version[0] and not os.path.exists(os.path.join(src,*version)):
            copy_src(os.path.join(src,version[0].split('.')[0],*version[1:]), srootbase)
        else:
            copy_src(os.path.join(src,*version), srootbase)
    if not sroot:
        sroot = get_sroot(srootbase)

    if version == ['iceprod','master'] and os.path.isdir(sroot):
        myprint('iceprod/master - deleting sroot')
        shutil.rmtree(sroot)
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
        run_cmd(['git', 'checkout', 'tags/v0.12.1'], cwd=spack_path)

    fileMirror = Mirror(mirror)

    os.environ['SPACK_ROOT'] = spack_path
    spack_bin = os.path.join(spack_path,'bin','spack')

    # clear repos
    repo_yaml = os.path.join(spack_path,'etc/spack/repos.yaml')
    if os.path.exists(repo_yaml):
        os.remove(repo_yaml)

    # add HEP repo
    hep_repo_path = os.path.join(spack_path,'var/spack/repos/hep-spack')
    if not os.path.exists(hep_repo_path):
        url = 'https://github.com/HEP-SF/hep-spack.git'
        run_cmd(['git', 'clone', url, hep_repo_path])
        run_cmd([spack_bin, 'repo', 'add', '--scope', 'site',
                 hep_repo_path])

    # add custom repo
    repo_path = os.path.join(os.path.dirname(__file__),*version)+'-repo'
    if (not os.path.exists(repo_path)) and len(version) == 2 and '.' in version[1]:
        repo_path = os.path.join(os.path.dirname(__file__),version[0],'.'.join(version[1].split('.')[:2]))+'-repo'
    if (not os.path.exists(repo_path)) and len(version) > 1:
        repo_path = os.path.join(os.path.dirname(__file__),version[0])+'-repo'
    if (not os.path.exists(repo_path)) and '.' in version[0]:
        repo_path = os.path.join(os.path.dirname(__file__),'.'.join(version[0].split('.')[:2]),*version[1:])+'-repo'
    if (not os.path.exists(repo_path)) and '.' in version[0]:
        repo_path = os.path.join(os.path.dirname(__file__),version[0].split('.')[0],*version[1:])+'-repo'
    if not os.path.exists(repo_path): # last resort
        repo_path = os.path.join(os.path.dirname(__file__),'repo')
    try:
        run_cmd([spack_bin, 'repo', 'add', '--scope', 'site', repo_path])
    except Exception:
        pass

    # add mirror
    if mirror:
        # set up mirror
        try:
            if mirror.startswith('/'):
                mirror_path = 'file://'+mirror
                run_cmd([spack_bin, 'mirror', 'add', 'local_filesystem', mirror_path])
            else:
                run_cmd([spack_bin, 'mirror', 'add', 'remote_server', mirror])
        except Exception:
            pass

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

            cmd = [spack_bin, 'install', '-y', '-v', '--no-checksum']
            if 'CPUS' in os.environ:
                cmd.extend(['-j', os.environ['CPUS']])
            for name, package in packages.items():
                myprint('installing', name)
                fileMirror.download(package)
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
            fileMirror.download(package)
            run_cmd(cmd+package.split()+deps)

        # set up dirs
        for d in ('bin',):
            path = os.path.join(sroot, d)
            if not os.path.exists(path):
                os.makedirs(path)

        # set up view
        if compiler_package:
            run_cmd([spack_bin, 'view', '-d', 'false', 'soft', '-i', sroot, compiler_package])
            if not os.path.lexists(os.path.join(sroot,'bin','cc')):
                run_cmd(['ln','-s','gcc','cc'], cwd=os.path.join(sroot,'bin'))
        cmd = [spack_bin, 'view', 'soft', '-i', sroot]
        for name, package in packages.items():
            myprint('adding', name, 'to view')
            view_cmd = cmd+package.split()[:1]
            if compiler_package:
                view_cmd[-1] += '%'+compiler_package+'spack'
            run_cmd(view_cmd)

        # pip install
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), *version)+'-pip')
        if os.path.exists(path):
            cmd = ['pip3', 'install', '-r', path]
            run_cmd_sroot(cmd, srootbase, cwd=sroot)

    finally:
        # cleanup
        run_cmd([spack_bin,'clean','-s','-d'])

def num_cpus():
    ret = 1
    try:
        ret = int(os.environ['CPUS'])
    except Exception:
        pass
    return ret

def meta_download(url, dest, tag=None):
    """
    Metaproject download of a url to a dest.
    """
    print("   downloading", url, "to", dest)
    if os.path.exists(dest):
        shutil.rmtree(dest)

    if url.endswith('.git'):
        run_cmd(['git', 'clone', url, dest])
        run_cmd(['git', 'checkout', tag], cwd=dest)
    else:
        run_cmd(['svn', 'co', url, dest, '--username', 'icecube',
                 '--password', 'skua', '--no-auth-cache', '--non-interactive'])

    if not os.path.exists(dest):
        raise Exception('download failed')

def build_meta(dest, version, checkout=False):
    srootbase = os.path.join(dest,version.replace('-metaproject',''))
    sroot = get_sroot(srootbase)

    metaprojects = get_packages(os.path.join(os.path.dirname(__file__), version))
    for meta_name in metaprojects:
        myprint('working on', meta_name)
        meta,name = meta_name.split('/',1)

        install_dir = os.path.join(sroot, 'metaprojects', meta_name)

        trunk = False
        if meta == 'icetray':
            src_url = 'https://github.com/icecube/icetray.git'
            if name.startswith('V'):
                # these are old releases ported to git, and need special tag names
                name = 'tags/releases/'+name
            elif not name.startswith('v'):
                # this is a branch, so always rebuild
                trunk = True
        else:
            if 'RC' in name:
                src_url = 'http://code.icecube.wisc.edu/svn/meta-projects/%s/candidates/%s'%(meta,name)
            elif name not in ('trunk', 'stable'):
                src_url = 'http://code.icecube.wisc.edu/svn/meta-projects/%s/releases/%s'%(meta,name)
            else:
                src_url = 'http://code.icecube.wisc.edu/svn/meta-projects/%s/%s'%(meta,name)
                trunk = True

        if checkout:
            src_dir = os.path.join(srootbase, 'metaprojects', meta_name)
            if trunk or not os.path.exists(src_dir):
                meta_download(src_url, src_dir, tag=name)
            myprint('   checkout only, so skipping build of', meta_name)
            continue

        if (not trunk) and os.path.exists(install_dir):
            myprint('   skipping build of', meta_name, ' - already built')
            continue

        src_dir = tempfile.mkdtemp(dir=os.getcwd())
        build_dir = tempfile.mkdtemp(dir=os.getcwd())
        try:
            meta_download(src_url, src_dir, tag=name)

            cmd = ['cmake', '-DCMAKE_BUILD_TYPE=Release',
                   '-DINSTALL_TOOL_LIBS=OFF',
                   '-DCMAKE_INSTALL_PREFIX='+install_dir,
                   src_dir]
            run_cmd_sroot(cmd, srootbase, cwd=build_dir)

            cmd = ['make', '-j', str(num_cpus())]
            run_cmd_sroot(cmd, srootbase, cwd=build_dir)

            if trunk and os.path.exists(install_dir):
                shutil.rmtree(install_dir)
            cmd = ['make', 'install']
            run_cmd_sroot(cmd, srootbase, cwd=build_dir)
        finally:
            shutil.rmtree(build_dir)
            shutil.rmtree(src_dir)

if __name__ == '__main__':
    from optparse import OptionParser

    parser = OptionParser(usage="%prog [options] versions")
    parser.add_option("--src", help="base source path")
    parser.add_option("--dest", help="base dest path")
    parser.add_option("--checkout", action='store_true', help="metaproject checkout only")
    parser.add_option("--mirror", help="mirror location")
    (options, args) = parser.parse_args()
    if not args:
        parser.error("need to specify a version")

    for version in args:
        if version.endswith('-metaproject'):
            build_meta(options.dest, version, checkout=options.checkout)
        else:
            build(options.src, options.dest, version, mirror=options.mirror)
