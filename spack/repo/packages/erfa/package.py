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


class Erfa(AutotoolsPackage):
    """Essential Routines for Fundamental Astronomy."""

    homepage = "https://github.com/liberfa/erfa"
    url      = "https://github.com/liberfa/erfa/releases/download/v1.3.0/erfa-1.3.0.tar.gz"

    version('1.4.0', '6f67ea6e39c70337c5de980eb7409800')
    version('1.3.0', '62347926625ecefbe5911446baed6676')
    version('1.2.0', '63e8e694d53add33c16f3f494d2b65f4')
    version('1.1.1', 'f227ada197eda3e622f4ef7cf7cdbd5a')
    version('1.1.0', '80eefd129e32c8290627a5c925c1534a')
    version('1.0.1', '35d8cf096313ed4500349aab04e8ae07')
    version('1.0.0', '7fcc2f647a77b8c0c883ab244b389756')
    version('0.0.1', '3736c0ff155fec6baa3637f135737344')

    variant('shared', default=True, description='Build shared libraries')
    variant('static', default=True, description='Build static libraries')
    variant('pic', default=True, description='Build PIC libraries')

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
