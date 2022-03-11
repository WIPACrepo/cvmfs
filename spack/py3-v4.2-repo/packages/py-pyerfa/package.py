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


class PyPyerfa(PythonPackage):
    """Python bindings for ERFA."""
    homepage = "https://github.com/liberfa/pyerfa"
    url      = "https://pypi.io/packages/source/p/pyerfa/pyerfa-2.0.0.1.tar.gz"

    version('2.0.0.1', sha256='2fd4637ffe2c1e6ede7482c13f583ba7c73119d78bef90175448ce506a0ede30')

    depends_on('py-setuptools', type='build')
    depends_on('py-pip', type='build')
    depends_on('py-packaging', type='build')
    depends_on('py-wheel', type='build')
    depends_on('py-numpy', type=('build','run'))
    depends_on('erfa')
    
    @run_before('build')
    def set_build_deps(self):
        lib_dir = self.spec['erfa'].prefix.lib
        if 'LIBRARY_PATH' in env:
            lib_dir += ':'+env['LIBRARY_PATH']
        env['LIBRARY_PATH'] = lib_dir

    def setup_environment(self, spack_env, run_env):
        spack_env.set('PYERFA_USE_SYSTEM_LIBERFA', '1')

