"""
Build cvmfs versions >=v4.3 with spack.
Or IceProd versions >=v2.7.
"""

import sys
import os
import json
from pathlib import Path
import shutil
import tempfile
import time
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


def run_cmd_sroot(args, srootbase, **kwargs):
    """print and run a subprocess command, inside an sroot environment."""
    myprint('cmd:',args)
    cmd = 'eval $('+os.path.join(srootbase,'setup.sh')+') ; '
    cmd += ' '.join(args)
    subprocess.check_call(cmd, shell=True, **kwargs)


def run_cmd_source_env(source_script, lines):
    """print and run a subprocess command, inside a source environment (like spack)."""
    with tempfile.TemporaryDirectory() as d:
        script = os.path.join(d, 'run.sh')
        with open(script, 'w') as f:
            print('#!/bin/bash', file=f)
            print('set -e', file=f)
            print(f'. {source_script}', file=f)
            for line in lines:
                print(line, file=f)
        myprint('script:\n', open(script).read())
        subprocess.check_call(f'bash {script}', shell=True)


def get_sroot(dir_name):
    """Get the SROOT from dir/os_arch.sh"""
    code,output,error = run_cmd_output(os.path.join(dir_name,'os_arch.sh'), shell=True)
    if code != 0:
        raise Exception('Failed to find SROOT')
    return Path(dir_name) / output.strip()


def get_sroot_no_arch(dir_name, *args):
    """Get the SROOT witout ARCH"""
    s = get_sroot(dir_name, *args)
    return s.parent / '_'.join(s.name.split('_')[:2])


def copy_src(src, dest):
    """Copy anything from src to dest"""
    src = str(src)
    dest = str(dest)
    print("copy_src", src, dest)
    if not os.path.exists(dest):
        os.makedirs(dest)
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

    def download(self, package):
        if self.mirror_path and self.spack_bin:
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
    ret = 20
    try:
        ret = int(os.environ['CPUS'])
    except Exception:
        pass
    return ret


def relative_to(path1, path2):
    try:
        path1.relative_to(path2)
    except ValueError:
        return False
    return True


class Build:
    def __init__(self, src, dest, version, mirror=None, spack_tag=None, spack_target=None, compiler_target=None):
        myprint('building version', version)
        if 'PYTHONPATH' in os.environ:
            del os.environ['PYTHONPATH']

        self.src = Path(src)
        self.dest = Path(dest)

        self.version = version.split('/') if '/' in version else [version]

        myprint('spack tag:', spack_tag)
        self.spack_tag = spack_tag
        self.spack_target = spack_target if spack_target else 'x86_64_v2'
        self.compiler_target = compiler_target if compiler_target else self.spack_target
        os.environ['ARCH'] = self.spack_target

        sroot_arch = self.spack_target
        if self.version[0] == 'iceprod':
            sroot_arch = None

        srootbase = self.dest.joinpath(*self.version)
        try:
            sroot = get_sroot(str(srootbase))
        except Exception:
            sroot = None
        if (not sroot) or sroot == 'RHEL_7_x86_64' or not relative_to(sroot, '/cvmfs'):
            if self.version[0] == 'iceprod':
                copy_src(self.src / 'iceprod' / 'all', srootbase)
            elif '.' in self.version[0] and not self.src.joinpath(*self.version).exists():
                copy_src(self.src.joinpath(self.version[0].split('.')[0], *self.version[1:]), srootbase)
            else:
                copy_src(self.src.joinpath(*self.version), srootbase)
        if not sroot:
            sroot = get_sroot(str(srootbase))
        self.srootbase = srootbase
        self.sroot = sroot

        if self.version == ['iceprod','master'] and self.sroot.is_dir():
            myprint('iceprod/master - deleting sroot '+str(self.sroot))
            shutil.rmtree(self.sroot)
        if not self.sroot.is_dir():
            self.sroot.mkdir(parents=True)

        # set up spack
        self.spack_path = self.sroot / 'spack'
        if not self.spack_path.is_dir():
            url = 'https://github.com/spack/spack.git'
            run_cmd(['git', 'clone', '--depth', '1', '--branch', self.spack_tag, url, str(self.spack_path)])

        os.environ['SPACK_ROOT'] = str(self.spack_path)
        self.spack_bin = str(self.spack_path / 'bin' / 'spack')

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
        icecube_repo_path = self.spack_path / 'var/spack/repos/icecube'
        if icecube_repo_path.exists():
            shutil.rmtree(icecube_repo_path)
        copy_src(repo_path, icecube_repo_path)
        ret,out,err = run_cmd_output([self.spack_bin, 'repo', 'list', '--scope', 'site'])
        if any(line.startswith('repo ') for line in out.split('\n')):
            run_cmd([self.spack_bin, 'repo', 'rm', '--scope', 'site', 'repo'])
        run_cmd([self.spack_bin, 'repo', 'add', '--scope', 'site', icecube_repo_path])

        # add mirror
        self.fileMirror = Mirror(mirror, spack_bin=self.spack_bin)
        if mirror:
            ret,out,err = run_cmd_output([self.spack_bin, 'mirror', 'list'])
            # set up mirror
            if mirror.startswith('/'):
                mirror_path = 'file://'+mirror
                if mirror_path not in out:
                    run_cmd([self.spack_bin, 'mirror', 'add', 'local_filesystem', mirror_path])
            else:
                if mirror not in out:
                    run_cmd([self.spack_bin, 'mirror', 'add', 'remote_server', mirror])

        ret = run_cmd_output([self.spack_bin, 'arch'])[1].split('-')
        self.spack_arch = {
            'platform': ret[0],
            'platform_os': ret[1],
            'target': self.spack_target
        }
        self.compiler_arch = {
            'platform': ret[0],
            'platform_os': ret[1],
            'target': self.compiler_target
        }

        self.setup_compiler()
        self.setup_env()
        self.setup_view()
        self.setup_python()

        # make I3_DATA symlinks
        i3_data = self.dest / 'data'
        for path in ('etc/vomsdir', 'etc/vomses', 'share/certificates', 'share/vomsdir'):
            basedir = self.sroot / os.path.dirname(path)
            if not basedir.exists():
                basedir.mkdir(parents=True)
            link = self.sroot / path
            if not os.path.lexists(link):
                (self.sroot / path).symlink_to(i3_data / 'voms' / path)

    def setup_compiler(self):
        # find system compiler first
        run_cmd([self.spack_bin, 'compiler', 'find', '--scope=site'])

        # setup compiler
        compiler_package = ''
        path = os.path.join(os.path.dirname(__file__), *self.version)+'-compiler'
        if not os.path.exists(path):
            myprint('skipping compiler install, as', path, 'is missing')
        else:
            packages = get_packages(path)
            compiler_name = None
            for name, package in packages.items():
                if 'gcc' in name or 'llvm' in name or 'nvhpc' in name:
                    compiler_name = name
                    compiler_package = package.split()[0]
            if not compiler_package:
                raise Exception('could not find compiler package name')
            
            cmd = [self.spack_bin, 'find', '--json']
            for pkg in json.loads(run_cmd_output(cmd)[1]):
                if pkg['name'] == compiler_name and pkg['arch'] == self.compiler_arch:
                    myprint('compiler', compiler_name, 'already installed')
                    break
            else:
                cmd = [self.spack_bin, 'install', '-y', '-v', '--no-checksum', '-j', str(num_cpus())]
                for name, package in packages.items():
                    myprint('installing', name)
                    self.fileMirror.download(package)
                    run_cmd(cmd+package.split()+['target='+self.compiler_target])
        self.compiler_package = compiler_package

        # add compiler to spack's list of compilers
        if compiler_package:
            self.compiler_package_with_arch = f'{compiler_package} arch={self.compiler_arch["platform"]}-{self.compiler_arch["platform_os"]}-{self.compiler_arch["target"]}'

            cmd = [self.spack_bin, 'compiler', 'list']
            needs_install = True
            platform_os = ''
            for line in run_cmd_output(cmd)[1].split('\n'):
                if line.startswith('--'):
                    platform_os = line.replace('-', ' ').strip().split()[1]
                if line.startswith('gcc'):
                    for comp in line.split():
                        if comp == compiler_package and platform_os == self.compiler_arch['platform_os']:
                            needs_install = False
                            break
            if needs_install:
                self._add_compiler(self.compiler_package_with_arch)

    def _add_compiler(self, compiler):
        """
        Update the compiler config for spack.

        Args:
            compiler (str): name of compiler package
        """
        myprint('add_compiler', compiler)

        # get compiler
        code,output,error = run_cmd_output([self.spack_bin, 'location', '-i', compiler])
        loc = output.strip(' \n')
        if (not loc) or not os.path.exists(loc):
            raise Exception('cannot find compiler '+compiler)
        run_cmd([self.spack_bin, 'compiler', 'add', '--scope', 'site', loc])

    def setup_env(self):
        # create spack env
        env_name = self.sroot.name.replace('.','_')
        env_yaml = """# This is a Spack Environment file.
#
# It describes a set of packages to be installed, along with
# configuration settings.
spack:
  specs:
"""
        self.packages = get_packages(os.path.join(os.path.dirname(__file__), *self.version))
        for name, package in self.packages.items():
            if self.spack_target == 'aarch64' and name == 'fftw':
                # FFTW: libquadmath is not avaliable on ARM
                package = package.replace(',quad','')

            env_yaml += f'  - {package}\n'

        env_yaml += f"""
  view: false
  concretizer:
    targets:
      granularity: generic
      #host_compatible: false
    unify: true
    duplicates:
      strategy: none
  packages:
    all:
      require: '"""
        if self.compiler_package:
            env_yaml += f'%{self.compiler_package} '
        env_yaml += f"""arch={self.spack_arch["platform"]}-{self.spack_arch["platform_os"]}-{self.spack_arch["target"]}'"""
        if self.compiler_package:
            env_yaml += f"""
      compiler:: [{self.compiler_package}]"""
        env_path = self.spack_path / 'var' / 'spack' / 'environments' / env_name / 'spack.yaml'
        env_path.parent.mkdir(parents=True, exist_ok=True)
        with open(env_path, 'w') as f:
            f.write(env_yaml)

        # now build the env
        spack_env = str(self.spack_path / 'share' / 'spack' / 'setup-env.sh')
        cmds = [
            f'spack env activate {env_name}',
            'spack concretize -f',
            f'spack install -y -v --fail-fast -j {num_cpus()}',
        ]
        run_cmd_source_env(spack_env, cmds)

    def setup_view(self):
        # set up dirs
        for d in ('bin',):
            path = self.sroot / d
            if not path.exists():
                path.mkdir(parents=True)

        # set up view
        if self.compiler_package:
            run_cmd([self.spack_bin, 'view', '-d', 'false', 'soft', '-i', str(self.sroot), self.compiler_package_with_arch])
            run_cmd([self.spack_bin, 'view', '-d', 'false', 'soft', '-i', str(self.sroot), 'binutils'])
            if not os.path.lexists(self.sroot / 'bin' / 'cc'):
                run_cmd(['ln','-s','gcc','cc'], cwd=(self.sroot / 'bin'))
        cmd = [self.spack_bin, 'view', 'soft', '-i', str(self.sroot)]
        for name, package in self.packages.items():
            myprint('adding', name, 'to view')
            view_cmd = cmd+package.split()[:1]
            if self.compiler_package:
                view_cmd[-1] += '%'+self.compiler_package
            view_cmd[-1] += f' arch={self.spack_arch["platform"]}-{self.spack_arch["platform_os"]}-{self.spack_arch["target"]}'
            run_cmd(view_cmd)

    def setup_python(self):
        # pip install
        path = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), *self.version)+'-pip'))
        path_os = path.parent / (path.name + '-' + str(self.sroot.name))
        if path_os.is_file():
            myprint('pip install using', path_os.name)
            cmd = ['python', '-m', 'pip', 'install', '-r', str(path_os)]
        elif path.is_file():
            myprint('pip install using', path.name)
            cmd = ['python', '-m', 'pip', 'install', '-r', str(path)]
        else:
            myprint('no pip install')
            return
        run_cmd_sroot(cmd, str(self.srootbase), cwd=self.sroot)


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

def build_meta(dest, version, checkout=False, spack_target=None):
    srootbase = os.path.join(dest, version.replace('-metaproject',''))
    spack_target = spack_target if spack_target else 'x86_64_v2'
    os.environ['ARCH'] = spack_target
    sroot = str(get_sroot(str(srootbase)))

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
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('--src', help='base source path')
    parser.add_argument('--dest', help='base dest path')
    parser.add_argument('--checkout', action='store_true', help='metaproject checkout only')
    parser.add_argument('--mirror', help='mirror location')
    parser.add_argument('--spack-tag', default=None, help='spack tag')
    parser.add_argument('--spack-target', default=None, help='CPU arch to optimize for. ex: x86_64_v2 or neoverse_v2')
    parser.add_argument('--compiler-target', default=None, help='CPU arch to build compiler (may need to be lower than --spack-target)')
    parser.add_argument('versions', nargs='+', help='cvmfs versions to build')
    args = parser.parse_args()

    for version in args.versions:
        if version.endswith('-metaproject'):
            build_meta(args.dest, version,
                checkout=args.checkout,
                spack_target=args.spack_target,
            )
        #elif float(version.split('-')[1][1:3]) < 4.3:
        #    build_old(args.src, args.dest, version, mirror=args.mirror)
        else:
            spack_tag = args.spack_tag
            if not spack_tag:
                if version.startswith('py') and float(version.split('-')[1][1:3]) == 4.3:
                    spack_tag = 'v0.20.0'
                else:
                    spack_tag = 'v0.23.0'
            Build(args.src, args.dest, version,
                mirror=args.mirror,
                spack_tag=spack_tag,
                spack_target=args.spack_target,
                compiler_target=args.compiler_target,
            )
