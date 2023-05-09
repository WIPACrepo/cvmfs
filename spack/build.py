"""
Build cvmfs versions >=v4 with spack.
Or IceProd versions >=v2.5.0.
"""
from __future__ import print_function

import sys
import os
import json
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

def copy_src(src, dest):
    """Copy anything from src to dest"""
    print("copy_src")
    try:
        os.makedirs(dest)
    except Exception:
        pass
    for p in os.listdir(src):
        if p.startswith('.'):
            continue
        path = os.path.join(src, p)
        if os.path.isdir(path):
            copy_src(path, os.path.join(dest, p))
        else:
            shutil.copy2(path, dest)


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

def get_installed_packages(spack_bin, compiler='spack'):
    cmd = [spack_bin, 'find', '--show-full-compiler', '-lv']
    code,output,error = run_cmd_output(cmd)
    installed_packages = {}
    for line in output.split('\n'):
        line = line.strip()
        if (not line) or line.startswith('--') or line.startswith('==>'):
            continue
        parts = line.split()
        # test for our compiler
        if compiler not in parts[1].split('%',1)[-1]:
            continue
        name = parts[1].split('@',1)[0]
        hash = parts[0]
        installed_packages[name] = name+'/'+hash
    myprint('installed packages:', list(installed_packages))
    return installed_packages


def get_dependencies(spack_path, package, packages, compiler='spack'):
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
    spack_bin = os.path.join(spack_path, 'bin', 'spack')
    installed_packages = get_installed_packages(spack_bin, compiler)

    dependencies = set()
    ret = []
    success = False
    package_name = package.split('@')[0]
    for _ in range(50):
        cmd = [spack_bin, 'spec', '--reuse', '-j']+package.split()+ret
        code,output,error = run_cmd_output(cmd)
        success = code == 0

        if success:
            new_deps = set()
            raw = json.loads(output)
            if 'dependencies' not in raw['spec']['nodes'][0]:
                return [] 
            for dep_raw in raw['spec']['nodes'][0]['dependencies']:
                dep = dep_raw['name']
                if dep != package_name:
                    myprint('dep:', dep)
                    if dep in packages and dep not in installed_packages:
                        myprint('   found', packages[dep])
                        new_deps.add(dep)
                    #elif dep in installed_packages:
                    #    myprint('   installed', installed_packages[dep])
                    #    new_deps.add(dep)
            if new_deps == dependencies:
                break
            dependencies = new_deps
        else:
            for line in error.split('\n'):
                if line.startswith('==> Error:'):
                    if 'depend on' in line:
                        bad_deps = line.split('depend on')[-1].replace(', or ',',').replace(' or ',',').split(',')
                    elif 'not a valid dependency' in line:
                        bad_deps = [line.split(':', 1)[-1].lstrip().split(' ', 1)[0].strip("'")]
                    else:
                        print(error)
                        raise Exception('bad dependency error')
                    for d in bad_deps:
                        d = d.strip()
                        if d in dependencies:
                            myprint('removing dep:', d)
                            dependencies.remove(d)
                        else:
                            print(error)
                            raise Exception('bad dependencies')
                    break
            else:
                print(output)
                print(error)
                raise Exception('bad dependencies')

        ret = []
        for d in dependencies:
            #if d in installed_packages:
            #    parts = installed_packages[d].split()
            if d in packages:
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


def get_dependencies_v12(spack_path, package, packages, compiler='spack'):
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
    spack_bin = os.path.join(spack_path, 'bin', 'spack')
    installed_packages = get_installed_packages(spack_bin, compiler)

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
                        myprint('   found', packages[dep])
                        dependencies.add(dep)
                        break
                    elif dep in installed_packages:
                        myprint('   installed', installed_packages[dep])
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
                        myprint('dep:', dep)
                        if dep in packages:
                            myprint('   found', packages[dep])
                            new_deps.add(dep)
                        elif dep in installed_packages:
                            myprint('   installed', installed_packages[dep])
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
                                myprint('removing dep:', d)
                                dependencies.remove(d)
                            else:
                                print(error)
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
    

installed_packages_cache = {}
def is_installed(spack_path, package, compiler='spack'):
    """Check if a package is installed"""
    global installed_packages_cache
    name = package.split('@')[0]
    if name in installed_packages_cache:
        return True

    spack_bin = os.path.join(spack_path, 'bin', 'spack')
    installed_packages_cache = get_installed_packages(spack_bin, compiler)
    return name in installed_packages_cache

def uninstall(spack_path, sroot, package):
    """Uninstall package and remove from view"""
    global installed_packages_cache
    spack_bin = os.path.join(spack_path, 'bin', 'spack')
    cmd = [spack_bin, 'view', '-v', '-d', 'false', 'rm',
           '--no-remove-dependents', sroot, package]
    run_cmd(cmd)
    cmd = [spack_bin, 'uninstall', '-y', '-f', '-a', package]
    run_cmd(cmd)
    if package in installed_packages_cache:
        del installed_packages_cache[package]


class Mirror:
    def __init__(self, mirror_path, spack_bin=None):
        self.mirror_path = mirror_path
        self.spack_bin = spack_bin
        if mirror_path and mirror_path.startswith('/') and not spack_bin:
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
            except Exception as e:
                myprint('failed to add '+pkg_version+' to mirror', e)
                pass

def num_cpus():
    ret = 1
    try:
        ret = int(os.environ['CPUS'])
    except Exception:
        pass
    return ret

class Build:
    def __init__(self, src, dest, version, mirror=None):
        myprint('building version', version)
        if 'PYTHONPATH' in os.environ:
            del os.environ['PYTHONPATH']

        self.src = src
        self.dest = dest

        self.version = version.split('/') if '/' in version else [version]

        srootbase = os.path.join(dest, *self.version)
        try:
            sroot = get_sroot(srootbase)
        except Exception:
            sroot = None
        if (not sroot) or sroot == 'RHEL_7_x86_64' or not sroot.startswith('/cvmfs'):
            if self.version[0] == 'iceprod':
                copy_src(os.path.join(src,'iceprod','all'), srootbase)
            elif '.' in self.version[0] and not os.path.exists(os.path.join(src, *self.version)):
                copy_src(os.path.join(src, self.version[0].split('.')[0], *self.version[1:]), srootbase)
            else:
                copy_src(os.path.join(src, *self.version), srootbase)
        if not sroot:
            sroot = get_sroot(srootbase)
        self.srootbase = srootbase
        self.sroot = sroot

        if self.version == ['iceprod','master'] and os.path.isdir(self.sroot):
            myprint('iceprod/master - deleting sroot')
            shutil.rmtree(self.sroot)
        if not os.path.isdir(self.sroot):
            os.makedirs(self.sroot)

        if self.version[0].startswith('py3-') and float(self.version[0].split('-', 1)[1][1:4]) >= 4.3:
            self.spack_tag = 'v0.19.2'
            self.extra_pkg_opts = ['target=x86_64_v2']
        else:
            self.spack_tag = 'v0.12.1'
            self.extra_pkg_opts = []

        # make I3_DATA symlinks
        i3_data = os.path.join(dest,'data')
        for path in ('etc/vomsdir', 'etc/vomses', 'share/certificates', 'share/vomsdir'):
            basedir = os.path.join(self.sroot, os.path.dirname(path))
            if not os.path.isdir(basedir):
                os.makedirs(basedir)
            if not os.path.lexists(os.path.join(self.sroot, path)):
                os.symlink(os.path.join(i3_data, 'voms', path),
                           os.path.join(self.sroot, path))

        # set up spack
        self.spack_path = os.path.join(self.sroot, 'spack')
        if not os.path.exists(self.spack_path):
            url = 'https://github.com/spack/spack.git'
            run_cmd(['git', 'clone', '--depth', '1', '--branch', self.spack_tag, url, self.spack_path])

        os.environ['SPACK_ROOT'] = self.spack_path
        self.spack_bin = os.path.join(self.spack_path, 'bin', 'spack')

        self.fileMirror = Mirror(mirror, spack_bin=(self.spack_bin if self.spack_tag != 'v0.12.1' else None))

        # clear repos
        repo_yaml = os.path.join(self.spack_path, 'etc/spack/repos.yaml')
        if os.path.exists(repo_yaml):
            os.remove(repo_yaml)

        # add HEP repo
        hep_repo_path = os.path.join(self.spack_path, 'var/spack/repos/hep-spack')
        if not os.path.exists(hep_repo_path):
            url = 'https://github.com/HEP-SF/hep-spack.git'
            run_cmd(['git', 'clone', url, hep_repo_path])
            run_cmd([self.spack_bin, 'repo', 'add', '--scope', 'site',
                     hep_repo_path])

        # add custom repo
        repo_path = os.path.join(os.path.dirname(__file__), *self.version)+'-repo'
        if (not os.path.exists(repo_path)) and len(self.version) == 2 and '.' in self.version[1]:
            repo_path = os.path.join(os.path.dirname(__file__), self.version[0], '.'.join(self.version[1].split('.')[:2]))+'-repo'
        if (not os.path.exists(repo_path)) and len(self.version) > 1:
            repo_path = os.path.join(os.path.dirname(__file__), self.version[0])+'-repo'
        if (not os.path.exists(repo_path)) and '.' in self.version[0]:
            repo_path = os.path.join(os.path.dirname(__file__), '.'.join(self.version[0].split('.')[:2]), *self.version[1:])+'-repo'
        if (not os.path.exists(repo_path)) and '.' in version[0]:
            repo_path = os.path.join(os.path.dirname(__file__), self.version[0].split('.')[0], *self.version[1:])+'-repo'
        if not os.path.exists(repo_path): # last resort
            repo_path = os.path.join(os.path.dirname(__file__), 'repo')
        try:
            run_cmd([self.spack_bin, 'repo', 'add', '--scope', 'site', repo_path])
        except Exception:
            pass

        # add mirror
        if mirror:
            # set up mirror
            try:
                if mirror.startswith('/'):
                    mirror_path = 'file://'+mirror
                    run_cmd([self.spack_bin, 'mirror', 'add', 'local_filesystem', mirror_path])
                else:
                    run_cmd([self.spack_bin, 'mirror', 'add', 'remote_server', mirror])
            except Exception:
                pass

        try:
            self.setup_compiler()
            self.setup_packages()
            self.setup_view()
            self.setup_python()
        finally:
            # cleanup
            run_cmd([self.spack_bin, 'clean', '-s', '-d'])

    def setup_compiler(self):
        # setup compiler
        compiler_package = ''
        path = os.path.join(os.path.dirname(__file__), *self.version)+'-compiler'
        if not os.path.exists(path):
            myprint('skipping compiler install, as', path, 'is missing')
        else:
            packages = get_packages(path)
            for name, package in packages.items():
                if 'gcc' in name or 'llvm' in name:
                    compiler_package = package.split()[0]
            if not compiler_package:
                raise Exception('could not find compiler package name')
            self._disable_compiler(compiler_package)

            cmd = [self.spack_bin, 'install', '-y', '-v', '--no-checksum', '-j', str(num_cpus())]
            for name, package in packages.items():
                myprint('installing', name)
                self.fileMirror.download(package)
                run_cmd(cmd+package.split()+self.extra_pkg_opts)
            self._update_compiler(compiler_package)
        self.compiler_package = compiler_package

    def _disable_compiler(self, compiler):
        """
        Disable the compiler config for spack.

        Args:
            compiler (str): name of compiler package
        """
        myprint('disable_compiler',compiler)

        if self.spack_tag != 'v0.12.1':
            try:
                run_cmd([self.spack_bin, 'compiler', 'remove', compiler])
            except Exception:
                pass
        else:
            # get arch
            code,output,error = run_cmd_output([self.spack_bin, 'arch'])
            spack_arch = output.strip(' \n')
            platform = spack_arch.split('-')[1]

            # update compilers.yaml
            compiler_cfg = os.path.join(self.spack_path, 'etc', 'spack', 'compilers.yaml')
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
            packages_cfg = os.path.join(self.spack_path, 'etc', 'spack', 'packages.yaml')
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

    def _update_compiler(self, compiler):
        """
        Update the compiler config for spack.

        Args:
            compiler (str): name of compiler package
        """
        myprint('update_compiler',compiler)

        # get compiler
        code,output,error = run_cmd_output([self.spack_bin, 'location', '-i', compiler])
        loc = output.strip(' \n')
        if (not loc) or not os.path.exists(loc):
            raise Exception('cannot find compiler '+compiler)

        if self.spack_tag != 'v0.12.1':
            run_cmd([self.spack_bin, 'compiler', 'add', loc])
        else:
            # get arch
            code,output,error = run_cmd_output([self.spack_bin, 'arch'])
            spack_arch = output.strip(' \n')
            platform = spack_arch.split('-')[1]

            # update compilers.yaml
            compiler_cfg = os.path.join(self.spack_path, 'etc', 'spack', 'compilers.yaml')
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
            packages_cfg = os.path.join(self.spack_path, 'etc', 'spack', 'packages.yaml')
            if os.path.exists(packages_cfg):
                with open(packages_cfg) as f:
                    packages_txt = f.read()
            else:
                packages_txt = 'packages:\n  all:\n'
            if 'compiler' not in packages_txt:
                packages_txt = packages_txt.replace('all:', 'all:\n    compiler: [{}spack]'.format(compiler))
                with open(packages_cfg,'w') as f:
                    f.write(packages_txt)

    def setup_packages(self):
        # install packages
        packages = get_packages(os.path.join(os.path.dirname(__file__), *self.version))
        cmd = [self.spack_bin, 'install', '-y', '-v', '--no-checksum', '-j', str(num_cpus())]
        if self.spack_tag != 'v0.12.1':
            cmd.append('--reuse')
        for name, package in packages.items():
            myprint('installing', name)
            main_pkg = package.split()[0]
            installed = is_installed(self.spack_path, main_pkg, compiler=self.compiler_package)
            if '@develop' in main_pkg and installed:
                uninstall(self.spack_path, self.sroot, main_pkg)
            elif installed:
                myprint(name, 'already installed')
                continue
            if self.spack_tag != 'v0.12.1':
                deps = get_dependencies(self.spack_path, package, packages, compiler=self.compiler_package)
            else:
                deps = get_dependencies_v12(self.spack_path, package, packages, compiler=self.compiler_package)
            self.fileMirror.download(package)
            run_cmd(cmd+package.split()+self.extra_pkg_opts+deps)
        self.packages = packages

    def setup_view(self):
        # set up dirs
        for d in ('bin',):
            path = os.path.join(self.sroot, d)
            if not os.path.exists(path):
                os.makedirs(path)

        # set up view
        if self.compiler_package:
            run_cmd([self.spack_bin, 'view', '-d', 'false', 'soft', '-i', self.sroot, self.compiler_package])
            if not os.path.lexists(os.path.join(self.sroot,'bin','cc')):
                run_cmd(['ln','-s','gcc','cc'], cwd=os.path.join(self.sroot,'bin'))
        cmd = [self.spack_bin, 'view', 'soft', '-i', self.sroot]
        for name, package in self.packages.items():
            myprint('adding', name, 'to view')
            view_cmd = cmd+package.split()[:1]
            if compiler_package:
                view_cmd[-1] += '%'+self.compiler_package+'spack'
            run_cmd(view_cmd)

    def setup_python(self):
        # pip install
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), *self.version)+'-pip')
        if os.path.exists(path):
            cmd = ['pip3', 'install', '-r', path]
            run_cmd_sroot(cmd, self.srootbase, cwd=sroot)


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
        #elif float(version.split('-')[1][1:3]) < 4.3:
        #    build_old(options.src, options.dest, version, mirror=options.mirror)
        else:
            Build(options.src, options.dest, version, mirror=options.mirror)
