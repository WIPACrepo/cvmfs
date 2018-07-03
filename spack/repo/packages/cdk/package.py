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


class Cdk(AutotoolsPackage):
    """A library of curses widgets which can be linked into your application."""

    homepage = "http://invisible-island.net/cdk/"
    url      = "ftp://ftp.invisible-island.net/cdk/cdk-5.0-20160131.tgz"

    version('5.0-20180306', '3b52823d8a78c6d27d4be8839edd279e')
    version('5.0-20171209', 'df6e786fc0b1faa8e518f80121c941c9')
    version('5.0-20161210', 'fbacdf194d097d73a61f9556bb2dbe27')
    version('5.0-20160131', '3a519980fd3c5d04ecfc82259586d7c4')

    variant('shared', default=True, description='Build shared libraries')

    def configure_args(self):
        args = ['--without-x', '--enable-const']
        spec = self.spec

        if '+shared' in spec:
            args.append('--with-shared')
        else:
            args.append('--without-shared')

        return args
