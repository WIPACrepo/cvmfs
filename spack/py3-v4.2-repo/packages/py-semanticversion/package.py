# Copyright 2013-2018 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *


class PySemanticversion(PythonPackage):
    """A library implementing the 'SemVer' scheme.."""

    homepage = "https://github.com/rbarrois/python-semanticversion"
    url      = "https://pypi.io/packages/source/s/semantic_version/semantic_version-2.9.0.tar.gz"

    version('2.9.0', sha256='abf54873553e5e07a6fd4d5f653b781f5ae41297a493666b59dcf214006a12b2')

    depends_on('python@3.6:', when='@2.0:')
    depends_on('py-setuptools', type='build')
