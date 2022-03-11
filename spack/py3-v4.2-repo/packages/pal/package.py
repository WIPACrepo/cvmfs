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


class Pal(AutotoolsPackage):
    """Positional Astronomy Library."""

    homepage = "https://github.com/Starlink/pal"
    url      = "https://github.com/Starlink/pal/releases/download/v0.9.8/pal-0.9.8.tar.gz"

    def url_for_version(self, version):
        return 'https://github.com/Starlink/pal/releases/download/v{}/pal-{}.tar.gz'.format(version, version)

    version('develop', git='https://github.com/IceCube-SPNO/pal.git')
    version('0.9.8', sha256='d50183637d446bfb1f67b741ebdb66858abf7f40fe871f739d737c9ed8b4b3b4')

    variant('shared', default=True, description='Build shared libraries')
    variant('static', default=True, description='Build static libraries')
    variant('pic', default=True, description='Build PIC libraries')

    depends_on('sofa-c', when="@:develop")
    depends_on('erfa')
    
    depends_on('autoconf', when="@develop")
    depends_on('automake', when="@develop")
    depends_on('m4', when="@develop")
    depends_on('libtool', when="@develop")

    def configure_args(self):
        spec = self.spec
        args = []

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

        if not spec.version.isdevelop():
            args.append('--without-starlink')

        return args
