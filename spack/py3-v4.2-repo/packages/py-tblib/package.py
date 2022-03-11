# Copyright 2013-2018 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *


class PyTblib(PythonPackage):
    """Traceback serialization library."""

    homepage = "https://github.com/ionelmc/python-tblib"
    url      = "https://pypi.io/packages/source/t/tblib/tblib-1.7.0.tar.gz"

    version('1.7.0', sha256='059bd77306ea7b419d4f76016aef6d7027cc8a0785579b5aad198803435f882c')

    depends_on('python@3.6:')
    depends_on('py-setuptools', type='build')
    depends_on('py-pip', type='build')
