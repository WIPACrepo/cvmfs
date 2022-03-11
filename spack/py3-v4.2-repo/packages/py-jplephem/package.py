# Copyright 2013-2018 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *


class PyJplephem(PythonPackage):
    """Use a JPL ephemeris to predict planet positions.."""

    homepage = "https://github.com/brandon-rhodes/python-jplephem/"
    url      = "https://pypi.io/packages/source/j/jplephem/jplephem-2.17.tar.gz"

    version('2.17', sha256='e1c6e5565c4d00485f1063241b4d1eff044585c22b8e97fad0ff2f6efb8aaa27')

    depends_on('python@3.6:', when='@2.0:')
    depends_on('py-pip', type='build')
    depends_on('py-numpy', type=('build', 'run'))
