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


class PyHtcondor(PythonPackage):
    """The HTCondor python modules aim to expose a high-quality, Pythonic
    interface to the HTCondor client libraries."""
    homepage = "https://htcondor-python.readthedocs.io"
    url = 'https://files.pythonhosted.org/packages/a5/fd/585d398ec544050b60449644aafef1b21e57feab5460b54313c9d5fb0c09/htcondor-8.7.9-cp36-cp36m-manylinux1_x86_64.whl'

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

