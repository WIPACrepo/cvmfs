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


class PyExtensionHelpers(PythonPackage):
    """Utilities for building and installing packages in the Astropy ecosystem."""
    homepage = "https://github.com/astropy/astropy-helpers"
    url      = "https://pypi.io/packages/source/e/extension-helpers/extension-helpers-0.1.tar.gz"

    version('0.1', sha256='ac8a6fe91c6d98986a51a9f08ca0c7945f8fd70d95b662ced4040ae5eb973882')

    depends_on('py-setuptools', type='build')
    depends_on('py-pip', type='build')
