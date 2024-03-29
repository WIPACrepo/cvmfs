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
import os

class Voms(AutotoolsPackage):
    """The VOMS native service and APIs """

    homepage = "https://github.com/italiangrid/voms"
    url      = "https://github.com/italiangrid/voms/archive/v2.0.14.tar.gz"

    version('2.0.14',    '3b07395e38a913e7b343a4d43666c428')
    version('2.0.13',    '13a5d9cdfdf3e8aa8aa32cf0b009a250')
    version('2.0.12-2',  'd7c3cb3dc9a3fe7baeedd1c944a5d77b')
    version('2.0.12',    '10e8e0b630470f01f497f27a01dd76b2')

    variant('shared', default=True, description='Build shared libraries')
    variant('static', default=True, description='Build static libraries')
    variant('pic', default=True, description='Build PIC libraries')

    variant('server', default=False, description='Enable server')
    variant('clients', default=True, description='Enable clients')
    variant('interfaces', default=False, description='Enable interfaces')

    depends_on('m4')
    depends_on('libtool')
    depends_on('autoconf')
    depends_on('automake')

    depends_on('openssl@1.0:1.0.99', when='@:2.0.14')
    depends_on('openssl@1.1:', when='@2.0.15:')
    depends_on('gsoap')

    @run_before('autoreconf')
    def mkdir_autoreconf(self):
        for d in ('aux', 'src/autogen'):
            try:
                os.makedirs(os.path.join(self.build_directory,d))
            except OSError:
                pass

    def configure_args(self):
        spec = self.spec
        args = ['--with-gsoap-wsdl2h={}'.format(os.path.join(spec['gsoap'].prefix.bin,'wsdl2h'))]

        if '+shared' in spec:
            args.append('--enable-shared')
        else:
            args.append('--disable-shared')

        if '+static' in spec:
            args.append('--enable-static')
        else:
            args.append('--disable-static')

        if '+pic' in spec:
            args.append('--with-pic')
        else:
            args.append('--without-pic')

        if '+server' in spec:
            args.append('--with-server')
        else:
            args.append('--without-server')

        if '+client' in spec:
            args.append('--with-client')
        else:
            args.append('--without-client')

        if '+interfaces' in spec:
            args.append('--with-interfaces')
        else:
            args.append('--without-interfaces')

        return args

