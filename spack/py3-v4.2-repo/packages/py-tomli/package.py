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
import os
import inspect
from spack import *
from spack.util import web



class PyTomli(PythonPackage):
    """Tomli is a Python library for parsing TOML. Tomli is fully compatible with TOML v1.0.0."""
    homepage = "https://github.com/hukkin/tomli/"
    url      = "https://files.pythonhosted.org/packages/97/75/10a9ebee3fd790d20926a90a2547f0bf78f371b2f13aa822c759680ca7b9/tomli-2.0.1-py3-none-any.whl"

    version('2.0.1', sha256='939de3e7a6161af0c887ef91b7d41a53e7c5a1ca976325f429cb46ea9bc30ecc', expand=False)

    def url_for_version(self, version):
        base_url = 'https://pypi.org/simple/tomli/'
        filename = 'tomli-{}-py3-none-any.whl'.format(version)

        response = web._urlopen(base_url)
        readme = response.read().decode('utf-8')
        name = None
        for line in readme.split('\n'):
            if filename in line:
                return line.split('=',1)[-1].split('>',1)[0].strip('"\' ').split('#')[0]
        else:
            raise Exception('cannot find version')

    depends_on('py-setuptools', type='build')
    depends_on('py-pip', type='build')

    phases = ['install']

    def install(self, spec, prefix):
        """Install everything from build directory."""
        python = inspect.getmodule(self).python

        with working_dir(self.build_directory):
            whl = None
            for f in os.listdir(self.build_directory):
                if f.endswith('whl'):
                    whl = f
                    break
            if not whl:
                raise Exception('cannot find wheel')
            python('-m', 'pip', 'install', '--disable-pip-version-check', '-v', '--no-deps', '--prefix={0}'.format(prefix), whl)
