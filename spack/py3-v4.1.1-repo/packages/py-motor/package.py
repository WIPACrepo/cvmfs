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


class PyMotor(PythonPackage):
    """Motor is a full-featured, non-blocking MongoDB driver for Python
    Tornado and asyncio applications."""
    homepage = "https://github.com/mongodb/motor/"
    url      = "https://pypi.io/packages/source/m/motor/motor-2.0.0.tar.gz"

    version('2.0.0', sha256='d035c09ab422bc50bf3efb134f7405694cae76268545bd21e14fb22e2638f84e')

    depends_on('py-setuptools', type='build')
    depends_on('py-mongo@3.6:4.0', type=('build', 'run'))
