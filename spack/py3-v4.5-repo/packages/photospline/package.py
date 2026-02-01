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
from spack_repo.builtin.build_systems.cmake import CMakePackage
from spack.package import *

class Photospline(CMakePackage):
    """Photospline is a library that uses the penalized spline technique
    to efficiently compute, store, and evaluate B-spline representations."""

    # Photospline is part of the spack packages, just not updated

    homepage = "https://github.com/IceCubeOpenSource/photospline"
    url      = "https://github.com/IceCubeOpenSource/photospline/archive/v2.0.4.tar.gz"

    license("BSD-2-Clause")

    version("2.4.2", 
    sha256="b3873fa475434b6ff3e1013a638d5a04970d21ced5ef32af5dd6a6f4fbb79b0c")
    version("2.4.1", sha256="c8bfd2a087300f3f217cecfe3e4354be4e2a485dfc503420c8ebbffeec5adf03")
    version("2.3.1", sha256="5d8cc8b54880092721122f4498b16ab63fdfbcf84b87df1c6a7992ece7baf9fe")
    version("2.2.1", sha256="2b455daf8736d24bf57cae9eb67d48463a6c4bd6a66c3ffacf52296454bb82ad")
    version("2.2.0", sha256="81f79b42fd63e12c13cc369fb5c6ef356389f7c7aaa10a584aae2e22dba79ccf")
    version("2.1.1", sha256="0a0dae8e1b994a35be23896982bd572fa97c617ad55a99b3da34782ad9435de8")
    version("2.1.0", sha256="bd6c58df8893917909b79ef2510a2043f909fbb7020bdace328d4d36e0222b60")
    version("2.0.7", sha256="59a3607c4aa036c55bcd233e8a0ec11575bd74173f3b4095cc6a77aa50baebcd")
    version("2.0.6", sha256="2f87c377e548f5fb44f8090c7559b2895f463a395b40a3276a04db44f39b1a4d")
    version("2.0.5", sha256="7e2679fac733fb4d881ff9d16fc99348a62b421811f256641f2449b98a6fb041")
    version("2.0.4", sha256="0a675ffe27e1d99fe482cdd7692320d6852c11c9a63de7e710ba075989e0bfb5")
    version("2.0.3", sha256="7045a631c41489085037b05fac98fd9cad73dc4262b7eead143d09e5f8265dec")
    version("2.0.2", sha256="0a3368205a7971a6919483ad5b5f0fbebb74614ec1891c95bb6a4fc9d3b950d4")
    version('2.0.1', '976b07481bb2a058c3751f5ef3844654')

    # This is reequired for spack to pick up the package
    depends_on("c", type="build")  # generated
    depends_on("cxx", type="build")  # generated

    depends_on('cfitsio')
    depends_on('openblas')
    depends_on('suite-sparse')
    depends_on('python')
    depends_on('py-numpy')

    def cmake_args(self):
        args = []
        return args
