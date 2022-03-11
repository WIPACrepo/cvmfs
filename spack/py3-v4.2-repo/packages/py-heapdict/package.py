# Copyright 2013-2018 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *


class PyHeapdict(PythonPackage):
    """Traceback serialization library."""

    homepage = "https://github.com/DanielStutzbach/heapdict"
    url      = "https://pypi.io/packages/source/h/heapdict/HeapDict-1.0.1.tar.gz"

    version('1.0.1', sha256='8495f57b3e03d8e46d5f1b2cc62ca881aca392fd5cc048dc0aa2e1a6d23ecdb6')

    depends_on('python@3.6:')
    depends_on('py-setuptools', type='build')
    depends_on('py-pip', type='build')
