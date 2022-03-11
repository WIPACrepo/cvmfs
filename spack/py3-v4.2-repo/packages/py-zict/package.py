# Copyright 2013-2018 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *


class PyZict(PythonPackage):
    """Mutable mapping tools."""

    homepage = "http://zict.readthedocs.io/en/latest/"
    url      = "https://pypi.io/packages/source/z/zict/zict-2.1.0.tar.gz"

    version('2.1.0', sha256='15b2cc15f95a476fbe0623fd8f771e1e771310bf7a01f95412a0b605b6e47510')

    depends_on('python@3.6:')
    depends_on('py-setuptools', type='build')
    depends_on('py-pip', type='build')
    depends_on('py-heapdict', type=('build', 'run'))
