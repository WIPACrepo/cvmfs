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


class PyLdap3(PythonPackage):
    """ldap3 is a strictly RFC 4510 conforming LDAP V3 pure Python client
    library. The same codebase runs in Python 2, Python 3, PyPy and PyPy3."""
    homepage = "https://github.com/cannatag/ldap3"
    url      = "https://pypi.io/packages/source/l/ldap3/ldap3-2.5.2.tar.gz"

    version('2.5.2', sha256='3f67c83185b1f0df8fdf6b52fa42c55bc9e9b7120c8b7fec60f0d6003c536d18')

    depends_on('py-setuptools', type='build')
    depends_on('py-pyasn1@0.1.8:', type=('build', 'run'))
