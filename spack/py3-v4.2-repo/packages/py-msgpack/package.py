# Copyright 2013-2018 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *


class PyMsgpack(PythonPackage):
    """MessagePack (de)serializer."""

    homepage = "https://msgpack.org/"
    url      = "https://pypi.io/packages/source/m/msgpack/msgpack-1.0.3.tar.gz"

    version('1.0.3', sha256='51fdc7fb93615286428ee7758cecc2f374d5ff363bdd884c7ea622a7a327a81e')

    depends_on('python@3.6:')

    # not just build-time, requires pkg_resources
    depends_on('py-setuptools', type=('build', 'run'))
    depends_on('py-setuptools-scm', type=('build', 'run'))
    depends_on('py-pip', type=('build', 'run'))
    depends_on('py-wheel', type=('build', 'run'))
    depends_on('py-packaging', type=('build', 'run'))
    depends_on('py-cython', type=('build', 'run'))

