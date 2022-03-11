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


class PyPyfits(PythonPackage):
    """The PyFITS module is a Python library providing access to FITS files.
    FITS (Flexible Image Transport System) is a portable file standard widely
    used in the astronomy community to store images and tables."""
    homepage = "https://pyfits.readthedocs.io"
    url      = "https://pypi.io/packages/source/P/Pyfits/pyfits-3.5.tar.gz"

    version('3.5', sha256='4e668622d5a3c140590bc6cf8222afcd4d133dde3d6beda3b9c3c9539c5acf18')

    depends_on('py-setuptools', type='build')
    depends_on('py-pip', type='build')
    depends_on('py-wheel', type='build')

    # requirements from setup.py
    depends_on('py-numpy', type=('build', 'run'))
