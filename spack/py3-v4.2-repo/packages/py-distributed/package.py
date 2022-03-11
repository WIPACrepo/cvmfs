# Copyright 2013-2018 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *


class PyDistributed(PythonPackage):
    """Distributed scheduler for Dask."""

    homepage = "https://distributed.dask.org/"
    url      = "https://pypi.io/packages/source/d/distributed/distributed-2022.2.1.tar.gz"

    version('2022.2.1', sha256='fb62a75af8ef33bbe1aa80a68c01a33a93c1cd5a332dd017ab44955bf7ecf65b')

    depends_on('python@3.6:')
    depends_on('py-setuptools', type='build')
    depends_on('py-pip', type='build')
    depends_on('py-packaging', type='build')
    depends_on('py-click', type=('build', 'run'))
    depends_on('py-cloudpickle', type=('build', 'run'))
    depends_on('py-jinja2', type=('build', 'run'))
    depends_on('py-psutil@5.0:', type=('build', 'run'))
    depends_on('py-sortedcontainers', type=('build', 'run'))
    depends_on('py-tblib@1.6.0:', type=('build', 'run'))
    depends_on('py-toolz@0.8.2:', type=('build', 'run'))
    depends_on('py-tornado@6.0.3:', type=('build', 'run'))
    depends_on('py-zict@0.1.3:', type=('build', 'run'))
    depends_on('py-pyyaml', type=('build', 'run'))
