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


class Gsoap(AutotoolsPackage):
    """The gSOAP toolkit is an extensive suite of portable C and C++ software 
       to develop XML Web services with powerful type-safe XML data bindings."""

    homepage = "https://sourceforge.net/projects/gsoap2/"
    url      = "http://downloads.sourceforge.net/project/gsoap2/gsoap-2.8/gsoap_2.8.55.zip"

    def url_for_version(self, version):
        url = "http://downloads.sourceforge.net/project/gsoap2/gsoap-{}/gsoap_{}.zip"
        return url.format(version.up_to(2), version)

    version('2.8.68', '6606df5a579a68cef671b233e5d8f73c')
    version('2.8.67', '38712d80ea66e036f2c45fa6171b5783')
    version('2.8.66', '086991a12f329b1674ff8448f4a27431')
    version('2.8.65', '1fad3079b0a8c8618d28d6ba65eab82e')
    version('2.8.64', 'b428063c1a32679805d3396b2e32fc03')
    version('2.8.63', 'f6deabb161bd2e1ad409c68d4afd6582')
    version('2.8.62', '8fc63b13b2b3495084d2e897019bf489')
    version('2.8.61', 'b26af4c0b9d88dba3864b18688a08ce9')
    version('2.8.60', 'a72051ea53564ff7438a8b8222592981')
    version('2.8.59', 'af00304f7c9345ce83b32d45e7e601b1')
    version('2.8.58', '6cd523ff556a557b18f28be96f2a311e')
    version('2.8.57', '4588970a4aaa66023179527469d4d98c')
    version('2.8.56', '9ca8be30c515cd06834dc2bfbbd85581')
    version('2.8.55', '414bff2beae2c74edec4c3630902c1b0')

    variant('ssl', default=True, description='SSL/TLS Support')
    variant('shared', default=True, description='Build shared libraries')
    variant('static', default=False, description='Build static libraries')

    conflicts('+shared', when='+static')

    depends_on('zlib')
    depends_on('openssl', when='+ssl')
    depends_on('bison')
    depends_on('flex')

    parallel = False

    def configure_args(self):
        args = ['--disable-c-locale']
        spec = self.spec

        if '+ssl' in spec:
            args.append('--enable-ssl')
        else:
            args.append('--disable-ssl')

        if '+shared' in spec:
            args.append('--enable-shared')
        else:
            args.append('--disable-shared')

        if '+static' in spec:
            args.append('--enable-static')
        else:
            args.append('--disable-static')

        return args
