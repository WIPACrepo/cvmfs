##############################################################################
# Copyright (c) 2013-2018, Lawrence Livermore National Security, LLC.
# Produced at the Lawrence Livermore National Laboratory.
#
# This file is part of Spack.
# Created by Todd Gamblin, tgamblin@llnl.gov, All rights reserved.
# LLNL-CODE-647188
#
# For details, see https://github.com/spack/spack
# Please also see the NOTICE and LICENSE files for our notice and the LGPL.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License (as
# published by the Free Software Foundation) version 2.1, February 1999.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the IMPLIED WARRANTY OF
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the terms and
# conditions of the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##############################################################################
from spack import *


class PyBotocore(PythonPackage):
    """A low-level interface to a growing number of Amazon Web Services. The
    botocore package is the foundation for the AWS CLI as well as boto3."""
    homepage = "https://pypi.org/project/boto3/"
    url      = "https://pypi.io/packages/source/b/botocore/botocore-1.12.83.tar.gz"

    version('1.12.83', sha256='97026101d5a9aebdd1f1f1794a25ac5fbf5969823590ee1461fb0103bc796c33')

    depends_on('py-setuptools', type='build')

    # requirements from setup.py
    depends_on('py-jmespath@0.7.1:1.0.0', type=('build', 'run'))
    depends_on('py-docutils@0.10:', type=('build', 'run'))
