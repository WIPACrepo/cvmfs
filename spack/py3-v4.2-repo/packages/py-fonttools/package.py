# Copyright 2013-2021 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *


class PyFonttools(PythonPackage):
    """fontTools is a library for manipulating fonts, written in Python.
    The project includes the TTX tool, that can convert TrueType and OpenType fonts to
    and from an XML text format, which is also called TTX. It supports TrueType,
    OpenType, AFM and to an extent Type 1 and some Mac-specific formats."""

    homepage = "https://github.com/fonttools/fonttools"
    url      = "https://pypi.io/packages/source/f/fonttools/fonttools-4.28.5.zip"

    version('4.28.5', sha256='545c05d0f7903a863c2020e07b8f0a57517f2c40d940bded77076397872d14ca')

    depends_on('python@3.7:', type=('build', 'run'))
    depends_on('py-setuptools', type='build')
    depends_on('py-setuptools-scm', type='build')
    depends_on('py-wheel', type='build')
    depends_on('py-packaging', type='build')
    depends_on('py-pip', type='build')
