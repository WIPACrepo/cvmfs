# Copyright 2013-2018 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *


class PyAsdf(PythonPackage):
    """Python implementation of the ASDF Standard."""

    homepage = "https://github.com/asdf-format/asdf"
    url      = "https://pypi.io/packages/source/a/asdf/asdf-1.5.0.tar.gz"

    version('2.10.1', sha256='f7e569f29b3723939efec8164eb2ed7274bdd480b0b283d75833f0f59d108409')

    depends_on('python@3.6:', when='@2.0:')
    depends_on('py-setuptools', type='build')
    depends_on('py-pip', type='build')
    depends_on('py-wheel', type='build')
    depends_on('py-numpy', type=('build', 'run'))
    depends_on('py-jsonschema', type=('build', 'run'))
    depends_on('py-pyyaml', type=('build', 'run'))
    depends_on('py-semanticversion', type=('build', 'run'))
