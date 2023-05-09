##############################################################################
# Copyright (c) 2013-2018, Lawrence Livermore National Security, LLC.
# Produced at the Lawrence Livermore National Laboratory.
#
# This file is part of Spack.
# Created by Todd Gamblin, tgamblin@llnl.gov, All rights reserved.
# LLNL-CODE-647188
#
# For details, see https://github.com/spack/spack
# Please also see the NOTICE and LICENSE files for our notice and the LGPL.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License (as
# published by the Free Software Foundation) version 2.1, February 1999.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the IMPLIED WARRANTY OF
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the terms and
# conditions of the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##############################################################################
from spack import *
from spack.util import web

import os
import glob

class Healpix(Package):
    """Software for pixelization, hierarchical indexation, synthesis, analysis, and visualization of data on the sphere."""

    homepage = "http://healpix.sourceforge.net/"

    def url_for_version(self, version):
        base_url = 'https://master.dl.sourceforge.net/project/healpix/Healpix_{}/'.format(version)
        readme_url = base_url+'README'
        response = web._urlopen(readme_url)
        readme = response.read().decode('utf-8')
        name = None
        for line in readme.split('\n'):
            if 'tar.gz' in line:
                name = line.strip('\n :')
                break
        else:
            raise Exception('cannot find version')
        return base_url+name

    version('3.31', 'c0dc75e57f237b634fec97df55997918')

    variant('cxx', default=True, description='Build cxx library')

    depends_on('m4', when='+cxx')
    depends_on('libtool', when='+cxx')
    depends_on('autoconf', when='+cxx')
    depends_on('automake', when='+cxx')

    depends_on('cfitsio')
    depends_on('libsharp', when='+cxx @3.60:', type='build')

    def setup_environment(self, spack_env, run_env):
        spack_env.set('CFLAGS', '-fno-tree-fre -fPIC')
        spack_env.set('CPPFLAGS', '-fno-tree-fre -fPIC')

    def install(self, spec, prefix):
        # install C healpix
        c_makefile = 'src/C/subs/Makefile'
        filter_file(r'(\$\(SHLIB_LD\) \-o \$\@ \$\(OBJD\))', r'\1 \$(CFITSIO_LIBS)', c_makefile)

        mkdirp(prefix.bin)
        mkdirp(prefix.include)
        mkdirp(prefix.lib.pkgconfig)

        with working_dir('src/C/subs'):
            make('shared', 'CFITSIO_INCDIR='+spec['cfitsio'].prefix.include,
                 'CFITSIO_LIBDIR='+spec['cfitsio'].prefix.lib)
            make('install', 'LIBDIR='+prefix.lib, 'INCDIR='+prefix.include, parallel=False)
        with open(os.path.join(prefix.lib,'pkgconfig','chealpix.pc'), 'w') as f:
            f.write("""# HEALPix/C pkg-config file

prefix={0}
libdir=${{prefix}}/lib
includedir=${{prefix}}/include

Name: chealpix
Description: C library for HEALPix (Hierarchical Equal-Area iso-Latitude) pixelisation of the sphere
Version: {1}
URL: http://healpix.sourceforge.net
Requires: cfitsio
Libs: -L${{prefix}}/lib -lchealpix
Cflags: -I${{prefix}}/include -fPIC
""".format(prefix, spec.version))

        if spec.satisfies('+cxx'):
            # install cxx healpix
            with working_dir('src/cxx'):
                autoreconf()
                extra_conf = []
                if spec.satisfies('@3.60:'):
                    configure_fix = FileFilter("configure")
                    # Link libsharp static libs
                    configure_fix.filter(
                        r"^SHARP_LIBS=.*$",
                        'SHARP_LIBS="-L{0} -lsharp -lc_utils -lfftpack -lm"\nSHARP_CFLAGS="-I{1}"'.format(
                            spec["libsharp"].prefix.lib,
                            spec['libsharp'].prefix.include
                        ),
                    )
                else:
                    extra_conf.extend([
                          '--with-libcfitsio='+spec['cfitsio'].prefix,
                          '--with-libcfitsio-include='+spec['cfitsio'].prefix.include,
                          '--with-libcfitsio-lib='+spec['cfitsio'].prefix.lib
                    ])
                    
                configure('--prefix='+prefix, '--disable-openmp', *extra_conf)

                if spec.satisfies("@:3.59"):
                    filter_file(r'\-march\=native', '', 'config/config.auto')
                    filter_file(r'\-ffast\-math', '', 'config/config.auto')
                make()

                cc = Executable(self.compiler.cc)
                cmd = ['-shared','-o','auto/lib/libhealpix_cxx.so',
                       '-L'+spec['cfitsio'].prefix.lib,
                       '-Wl,--no-as-needed', '-lcfitsio',
                       '-Wl,--as-needed', '-Wl,--whole-archive']
                cmd += glob.glob('auto/lib/*.a')
                cmd += ['-Wl,--no-whole-archive']
                cc(*cmd)
                install = which('install')
                for root,dirs,files in os.walk('auto'):
                    base_cmd = ['-D']
                    p = os.path.basename(root)
                    if 'include' in root:
                        base_cmd += ['-m','644']
                        p = os.path.join(p,'healpix_cxx')
                    for f in files:
                        if not f.endswith('.a'):
                            cmd = list(base_cmd)
                            cmd += [os.path.join(root,f), os.path.join(prefix,p,f)]
                            install(*cmd)

            with open(os.path.join(prefix.lib,'pkgconfig','healpix_cxx.pc'), 'w') as f:
                f.write("""# HEALPix/C++ pkg-config file

prefix={0}
libdir=${{prefix}}/lib
includedir=${{prefix}}/include/healpix_cxx

Name: healpix_cxx
Description: C++ library for HEALPix (Hierarchical Equal-Area iso-Latitude) pixelisation of the sphere
Version: {1}
URL: http://healpix.sourceforge.net
Requires: cfitsio sharp
Libs: -L${{prefix}}/lib -lhealpix_cxx -lsharp
Cflags: -I${{prefix}}/include/healpix_cxx -fPIC
""".format(prefix, spec.version))
