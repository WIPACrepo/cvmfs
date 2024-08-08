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
    url = "https://master.dl.sourceforge.net/project/healpix/Healpix_3.82/Healpix_3.82_2022Jul28.tar.gz"

    def url_for_version(self, version):
        base_url = 'https://master.dl.sourceforge.net/project/healpix/Healpix_{}/'.format(version)
        readme_url = base_url+'README'
        
        response = web.read_from_url(readme_url)[-1]
        readme = response.read().decode('utf-8')
        name = None
        for line in readme.split('\n'):
            if 'tar.gz' in line:
                name = line.strip('\n :')
                break
        else:
            raise Exception('cannot find version')
        return base_url+name

    version('3.82', sha1='57b9963340af7c983040892c84d8f6d1a72dd22a')
    version('3.31', 'c0dc75e57f237b634fec97df55997918')

    variant('cxx', default=True, description='Build cxx library')

    depends_on('m4', when='+cxx @:3.59')
    depends_on('libtool', when='+cxx @:3.59')
    depends_on('autoconf', when='+cxx @:3.59')
    depends_on('automake', when='+cxx @:3.59')

    depends_on('cfitsio')

    conflicts('libsharp', msg='libsharp is built internally')
    conflicts('^cfitsio@4:',
        when='@:3.8',
        msg='cfitsio v4 requires 3.80+'
    )

    def setup_environment(self, spack_env, run_env):
        spack_env.set('CFLAGS', '-fno-tree-fre -fPIC')
        spack_env.set('CPPFLAGS', '-fno-tree-fre -fPIC')

    def install(self, spec, prefix):
        if spec.satisfies('@3.60:'):
            # new builds, all in one
            filter_file(r'^prefix=.*$', f'prefix={prefix}', 'hpxconfig_functions.sh')
            filter_file(r'^\s*SHARPPREFIX=.*$', f'SHARPPREFIX={prefix}', 'hpxconfig_functions.sh')
            filter_file(r'SHARP_CFLAGS="-I\$\{HEALPIX\}/include"', f'SHARP_CFLAGS="-I{prefix.include}"', 'hpxconfig_functions.sh')
            filter_file(r'SHARP_LIBS="-L\$\{HEALPIX\}/lib', f'SHARP_LIBS="-L{prefix.lib}', 'hpxconfig_functions.sh')
            filter_file(r'^\s*CXXPREFIX=.*$', f'CXXPREFIX={prefix}', 'hpxconfig_functions.sh')
            filter_file(r'^\s*C_SHARED\s*=.*$', 'C_SHARED=1', 'hpxconfig_functions.sh')
            filter_file(r'^\s*F_PARAL\s*=.*$', 'F_PARAL=0', 'hpxconfig_functions.sh')
            filter_file(r'^\s+findFITSLib.*$', f'findFITSLib {self.spec["cfitsio"].prefix.lib}', 'hpxconfig_functions.sh')
            filter_file(r'^\s+findFITSInclude.*$', f'findFITSInclude {self.spec["cfitsio"].prefix.include}', 'hpxconfig_functions.sh')
            filter_file(r'^\s*FITSPREFIX\s*=.*$', f'FITSPREFIX="{self.spec["cfitsio"].prefix}"', 'hpxconfig_functions.sh')
            filter_file(r'^\s*SHARP_COPT\s*=.*$', 'SHARP_COPT="-O3"', 'hpxconfig_functions.sh')
            filter_file(r'^\s*SHARP_PARAL\s*=.*$', 'SHARP_PARAL=0', 'hpxconfig_functions.sh')
            filter_file(r'^\s*CXX_PARAL\s*=.*$', 'CXX_PARAL=0', 'hpxconfig_functions.sh')
            auto_list = ['c', 'profile']
            if spec.satisfies('+cxx'):
                auto_list.extend(['cxx', 'sharp'])
            configure('-h')
            configure('-L', '--auto=' + ','.join(auto_list))
            make()
        else:
            # old build instructions with manual component building
            
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
                    configure('--prefix='+prefix, '--disable-openmp', 
                          '--with-libcfitsio='+spec['cfitsio'].prefix,
                          '--with-libcfitsio-include='+spec['cfitsio'].prefix.include,
                          '--with-libcfitsio-lib='+spec['cfitsio'].prefix.lib
                    )

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
