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



class PyDistlib(PythonPackage):
    """Distlib is a library which implements low-level functions that relate to packaging and distribution of Python software. It is intended to be used as the basis for third-party packaging tools."""
    homepage = "https://github.com/pypa/distlib"
    url      = "https://files.pythonhosted.org/packages/58/07/815476ae605bcc5f95c87a62b95e74a1bce0878bc7a3119bc2bf4178f175/distlib-0.3.6.tar.gz"

    version('0.3.6', sha256='14bad2d9b04d3a36127ac97f30b12a19268f211063d8f8ee4f47108896e11b46', expand=False)

    def url_for_version(self, version):
        base_url = 'https://pypi.org/simple/distlib/'
        filename = 'distlib-{}-py2.py3-none-any.whl'.format(version)

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
    depends_on('py-wheel', type='build')
    depends_on('py-tomli', type='build')

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
