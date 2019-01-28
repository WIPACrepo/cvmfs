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


class PyIceprod(PythonPackage):
    """IceProd is a Python framework for distributed management of batch jobs.
    It runs as a layer on top of other batch middleware, such as HTCondor, and
    can pool together resources from different batch systems. The primary
    purpose is to coordinate and administer many large sets of jobs at once,
    keeping a history of the entire job lifecycle."""
    homepage = "https://github.com/WIPACrepo/iceprod/"
    url      = "https://github.com/WIPACrepo/iceprod/archive/v2.5.0.tar.gz"
    git      = "https://github.com/WIPACrepo/iceprod.git"

    def url_for_version(self, version):
        url = "https://github.com/WIPACrepo/iceprod/archive/v{0}.tar.gz"
        return url.format(version)

    version('develop', branch='master')
    version('2.5.0', sha256='ac548773db2989d69a2789326101f26bbafba29d0d70359a777fd4fc36c1d998')

    depends_on('py-setuptools', type='build')

    # requirements from setup.py
    depends_on('py-boto3', type=('build', 'run'))
    depends_on('py-certifi', type=('build', 'run'))
    depends_on('py-coverage', type=('build', 'run'))
    depends_on('py-cryptography', type=('build', 'run'))
    depends_on('py-htcondor', type=('build', 'run'))
    depends_on('py-jsonschema', type=('build', 'run'))
    depends_on('py-ldap3', type=('build', 'run'))
    depends_on('py-pyopenssl', type=('build', 'run'))
    depends_on('py-mongo@3.7.2', type=('build', 'run'))
    depends_on('py-motor', type=('build', 'run'))
    depends_on('py-pyasn1', type=('build', 'run'))
    depends_on('py-pyjwt', type=('build', 'run'))
    depends_on('py-requests', type=('build', 'run'))
    depends_on('py-requests-toolbelt', type=('build', 'run'))
    depends_on('py-requests-futures', type=('build', 'run'))
    depends_on('py-rest-tools', type=('build', 'run'))
    depends_on('py-sphinx', type=('build', 'run'))
    depends_on('py-statsd', type=('build', 'run'))
    depends_on('py-tornado@5.1:', type=('build', 'run'))
