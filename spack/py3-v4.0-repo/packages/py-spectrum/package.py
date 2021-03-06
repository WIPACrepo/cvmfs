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


class PySpectrum(PythonPackage):
    """Spectrum is a Python library that contains tools to estimate
    Power Spectral Densities based on Fourier transform, Parametric
    methods or eigenvalues analysis."""
    homepage = "https://pyspectrum.readthedocs.io"
    url      = "https://pypi.io/packages/source/s/spectrum/spectrum-0.7.4.tar.gz"

    version('0.7.4', sha256='a15d733c9e82a6572d0515ba49bc276119a215fe71c63538c38f121ff6c5b3d6')

    depends_on('py-setuptools', type='build')

    # requirements from setup.py
    depends_on('py-numpy', type=('build', 'run'))
    depends_on('py-scipy', type=('build', 'run'))
    depends_on('py-matplotlib', type=('build', 'run'))
