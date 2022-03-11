# Copyright 2013-2018 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *


class PyFsspec(PythonPackage):
    """File-system specification."""

    homepage = "http://github.com/fsspec/filesystem_spec"
    url      = "https://pypi.io/packages/source/f/fsspec/fsspec-2022.2.0.tar.gz"

    version('2022.2.0', sha256='20322c659538501f52f6caa73b08b2ff570b7e8ea30a86559721d090e473ad5c')

    depends_on('python@3.6:')
    depends_on('py-setuptools', type='build')
