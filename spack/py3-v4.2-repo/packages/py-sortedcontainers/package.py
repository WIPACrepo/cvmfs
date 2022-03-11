# Copyright 2013-2018 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *


class PySortedcontainers(PythonPackage):
    """Sorted Containers -- Sorted List, Sorted Dict, Sorted Set."""

    homepage = "http://github.com/mozilla/bleach"
    url      = "https://pypi.io/packages/source/s/sortedcontainers/sortedcontainers-2.4.0.tar.gz"

    version('2.4.0', sha256='25caa5a06cc30b6b83d11423433f65d1f9d76c4c6a0c90e3379eaa43b9bfdb88')

    depends_on('python@3.6:')
    depends_on('py-setuptools', type='build')
