# Copyright 2013-2018 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *


class PyPlatformdirs(PythonPackage):
    """A small Python module for determining appropriate platform-specific dirs, e.g. a "user data dir"."""

    homepage = "https://github.com/platformdirs/platformdirs"
    url      = "https://pypi.io/packages/source/p/platformdirs/platformdirs-2.5.1.tar.gz"

    version('2.5.1', sha256='7535e70dfa32e84d4b34996ea99c5e432fa29a708d0f4e394bbcb2a8faa4f16d')

    depends_on('python@3.6:')

    # not just build-time, requires pkg_resources
    depends_on('py-setuptools', type=('build', 'run'))
    depends_on('py-setuptools-scm', type=('build', 'run'))
    depends_on('py-pip', type=('build', 'run'))
    depends_on('py-wheel', type=('build', 'run'))
    depends_on('py-packaging', type=('build', 'run'))

