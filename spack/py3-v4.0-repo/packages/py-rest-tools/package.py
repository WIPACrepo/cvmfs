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


class PyRestTools(PythonPackage):
    """REST tools in python - common code for client and server"""
    homepage = "https://github.com/WIPACrepo/rest-tools"
    url      = "https://github.com/WIPACrepo/rest-tools/archive/v0.1.0.tar.gz"

    def url_for_version(self, version):
        url = "https://github.com/WIPACrepo/rest-tools/archive/v{0}.tar.gz"
        return url.format(version)

    version('0.1.0', sha256='c72c53a774f2549c9ace2b4d95d28acd291591273d017d8f86549b20c54c7a0e')

    depends_on('py-setuptools', type='build')
    depends_on('py-requests', type=('build', 'run'))
    depends_on('py-requests-futures', type=('build', 'run'))
    depends_on('py-pyjwt', type=('build', 'run'))
    depends_on('py-tornado@5.1:', type=('build', 'run'))
