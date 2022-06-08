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


class PyHtcondor(PythonPackage):
    """The HTCondor python modules aim to expose a high-quality, Pythonic
    interface to the HTCondor client libraries."""
    homepage = "https://htcondor-python.readthedocs.io"
    url = 'https://files.pythonhosted.org/packages/1c/84/eee7908ece043e93a3866b79abbe9be8338229d81652c849906967de6cb0/htcondor-8.8.6-cp37-cp37m-manylinux1_x86_64.whl'

    def url_for_version(self, version):
        base_url = 'https://pypi.org/simple/htcondor/'
        suffix = 'manylinux1_x86_64.whl'
        if self.version >= Version('9.4.0'):
            suffix = 'manylinux_2_12_x86_64.manylinux2010_x86_64.whl'
        elif self.version >= Version('9.0.1'):
            suffix = 'manylinux_2_5_x86_64.manylinux1_x86_64.whl'

        if self.spec.satisfies('^python@3.6:3.6.99'):
            filename = 'htcondor-{}-cp36-cp36m-{}'.format(version, suffix)
        elif self.spec.satisfies('^python@3.7:3.7.99'):
            filename = 'htcondor-{}-cp37-cp37m-{}'.format(version, suffix)
        elif self.spec.satisfies('^python@3.8:3.8.99'):
            filename = 'htcondor-{}-cp38-cp38-{}'.format(version, suffix)
        elif self.spec.satisfies('^python@3.9:3.9.99'):
            filename = 'htcondor-{}-cp39-cp39-{}'.format(version, suffix)
        elif self.spec.satisfies('^python@3.10:'):
            filename = 'htcondor-{}-cp310-cp310-{}'.format(version, suffix)


        response = web._urlopen(base_url)
        readme = response.read().decode('utf-8')
        name = None
        for line in readme.split('\n'):
            if filename in line:
                return line.split('=',1)[-1].split('>',1)[0].strip('"\' ').split('#')[0]
        else:
            raise Exception('cannot find version')

    version('8.9.11', sha256='fe568076cc3e4c20e7e77c03695c72d4082ccd14bb889e515ef7be9ac6bd3ad7', expand=False)
    version('8.8.6', sha256='226534187ddf4dcd05ae3dcdd5007f3f41654bc65a874b4a2cc14573f6f66b8e', expand=False)
    version('8.7.9', sha256='17ae9767bc74b6fb007666eafcacb03c14b1c521b3e154f9ebb053e14376eaa2', expand=False)

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

