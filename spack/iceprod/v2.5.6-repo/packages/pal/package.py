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

    homepage = "https://github.com/IceCube-SPNO/pal"
    url      = "https://github.com/IceCube-SPNO/pal.git"

    version('develop', git='https://github.com/IceCube-SPNO/pal.git')

    variant('shared', default=True, description='Build shared libraries')
    variant('static', default=True, description='Build static libraries')
    variant('pic', default=True, description='Build PIC libraries')

    depends_on('erfa')

    depends_on('autoconf')
    depends_on('automake')
    depends_on('m4')
    depends_on('libtool')

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

        return args
