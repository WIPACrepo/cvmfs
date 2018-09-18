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


class PyPymysql(PythonPackage):
    """PyMySQL is a pure-Python MySQL client library, based on PEP 249."""
    homepage = "https://pymysql.readthedocs.io"
    url      = "https://github.com/PyMySQL/PyMySQL/archive/v0.9.2.tar.gz"

    version('0.9.2', sha256='7d7eb459e7a2ae633a677e4b692a35fdafd2d816952f34fc1f3b967f40d1ac2a')
    version('0.9.1', sha256='cfd54cae5d4309ab741c2adfc9b001bc5b92fb669d8f6744d694c5cb20be4770')
    version('0.9.0', sha256='d1ea129058049cb2c545447d03cf4a0f28b98d5b789448edd575147e377b076e')
    version('0.8.1', sha256='6436a31edfbe15fd3b42e86115618dddf591b121290a391423f7cc1a662510f4')
    version('0.8.0', sha256='28db0f1acd35fcb4c4601c3c482bd962f5a5e8eb8838a499e6621da520f8a4b9')

    depends_on('py-setuptools', type='build')

    # requirements from setup.py
    depends_on('py-cryptography', type=('build', 'run'))
