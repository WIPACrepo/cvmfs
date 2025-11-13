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


class Photospline(CMakePackage):
    """Photospline is a library that uses the penalized spline technique
    to efficiently compute, store, and evaluate B-spline representations."""

    homepage = "https://github.com/IceCubeOpenSource/photospline"
    url      = "https://github.com/IceCubeOpenSource/photospline/archive/v2.0.4.tar.gz"

    version("2.4.1", sha256="c8bfd2a087300f3f217cecfe3e4354be4e2a485dfc503420c8ebbffeec5adf03")
    version("2.3.1", sha256="5d8cc8b54880092721122f4498b16ab63fdfbcf84b87df1c6a7992ece7baf9fe")
    version("2.1.1", sha256="0a0dae8e1b994a35be23896982bd572fa97c617ad55a99b3da34782ad9435de8")
    version('2.0.4', sha256='0a675ffe27e1d99fe482cdd7692320d6852c11c9a63de7e710ba075989e0bfb5')
    version('2.0.1', '976b07481bb2a058c3751f5ef3844654')

    depends_on('cfitsio')
    depends_on('openblas')
    depends_on('suite-sparse')
    depends_on('python')
    depends_on('py-numpy')

    def cmake_args(self):
        args = []
        return args
