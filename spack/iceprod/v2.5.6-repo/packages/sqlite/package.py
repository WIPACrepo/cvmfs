# Copyright 2013-2018 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)
import sys
from spack import *
from spack import architecture


class Sqlite(AutotoolsPackage):
    """SQLite3 is an SQL database engine in a C library. Programs that
       link the SQLite3 library can have SQL database access without
       running a separate RDBMS process.
    """
    homepage = "www.sqlite.org"

    version('3.23.1', '0edbfd75ececb95e8e6448d6ff33df82774c9646',
            url='https://www.sqlite.org/2018/sqlite-autoconf-3230100.tar.gz')
    version('3.22.0', '2fb24ec12001926d5209d2da90d252b9825366ac',
            url='https://www.sqlite.org/2018/sqlite-autoconf-3220000.tar.gz')
    version('3.21.0', '7913de4c3126ba3c24689cb7a199ea31',
            url='https://www.sqlite.org/2017/sqlite-autoconf-3210000.tar.gz')
    version('3.20.0', 'e262a28b73cc330e7e83520c8ce14e4d',
            url='https://www.sqlite.org/2017/sqlite-autoconf-3200000.tar.gz')
    version('3.18.0', 'a6687a8ae1f66abc8df739aeadecfd0c',
            url='https://www.sqlite.org/2017/sqlite-autoconf-3180000.tar.gz')
    version('3.8.10.2', 'a18bfc015cd49a1e7a961b7b77bc3b37',
            url='https://www.sqlite.org/2015/sqlite-autoconf-3081002.tar.gz')
    version('3.8.5', '0544ef6d7afd8ca797935ccc2685a9ed',
            url='https://www.sqlite.org/2014/sqlite-autoconf-3080500.tar.gz')

    def url_for_version(self, version):
        url = 'https://www.sqlite.org/{0}/sqlite-autoconf-{1}{2:02d}{3:02d}{4:02d}.tar.gz'

        if version < Version('3.8.8'):
            year = 2014
        elif version != Version('3.9.3') and version < Version('3.10.0'):
            year = 2015
        elif version < Version('3.16.0'):
            year = 2016
        elif version < Version('3.22.0'):
            year = 2017
        elif version < Version('3.27.0'):
            year = 2018
        elif version < Version('3.31.0'):
            year = 2019
        elif version < Version('3.34.1'):
            year = 2020
        else:
            year = 2021

        version_split = str(version.dotted).split('.')
        vals = [year]
        for i in range(4):
            vals.append(int(version_split[i]) if i < len(version_split) else 0)

        url = url.format(*vals)

        return url

    depends_on('readline')

    # On some platforms (e.g., PPC) the include chain includes termios.h which
    # defines a macro B0. Sqlite has a shell.c source file that declares a
    # variable named B0 and will fail to compile when the macro is found. The
    # following patch undefines the macro in shell.c
    patch('sqlite_b0.patch', when='@3.18.0:3.21.0')

    # Starting version 3.17.0, SQLite uses compiler built-ins
    # __builtin_sub_overflow(), __builtin_add_overflow(), and
    # __builtin_mul_overflow(), which are not supported by Intel compiler.
    # Starting version 3.21.0 SQLite doesn't use the built-ins if Intel
    # compiler is used.
    patch('remove_overflow_builtins.patch', when='@3.17.0:3.20%intel')

    variant('functions', default=False,
            description='Provide mathematical and string extension functions '
                        'for SQL queries using the loadable extensions '
                        'mechanism.')

    resource(name='extension-functions',
             url='https://sqlite.org/contrib/download/extension-functions.c/download/extension-functions.c?get=25',
             md5='3a32bfeace0d718505af571861724a43',
             expand=False,
             placement={'extension-functions.c?get=25':
                        'extension-functions.c'},
             when='+functions')

    @property
    def libs(self):
        return find_libraries('libsqlite3', root=self.prefix.lib)

    def get_arch(self):
        arch = architecture.Arch()
        arch.platform = architecture.platform()
        return str(arch.platform.target('default_target'))

    def configure_args(self):
        args = []

        if self.get_arch() == 'ppc64le':
            args.append('--build=powerpc64le-redhat-linux-gnu')

        return args

    @run_after('install')
    def build_libsqlitefunctions(self):
        if '+functions' in self.spec:
            libraryname = 'libsqlitefunctions.' + dso_suffix
            cc = Executable(spack_cc)
            cc(self.compiler.pic_flag, '-lm', '-shared',
                'extension-functions.c', '-o', libraryname)
            install(libraryname, self.prefix.lib)
