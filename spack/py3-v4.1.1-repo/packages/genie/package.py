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
from spack.util import web

import os
import glob

class Genie(AutotoolsPackage):
    """Event Generator & Global Analysis of Neutrino Scattering Data"""

    homepage = "http://www.genie-mc.org/"
    url = 'https://github.com/GENIE-MC/Generator/archive/R-2_12_10.tar.gz'

    version('3_00_00', sha256='3953c7d9f1f832dd32dfbc0b9260be59431206c204aec6ab0aa68c01176f2ae6')

    patch('compiler.patch', when='@3_00_00')
    patch('install.patch', when='@3_00_00')

    variant('lhapdf5', default=True,
        description='Use the LHAPDF5 parton density function library')
    variant('lhapdf6', default=False,
        description='Use the LHAPDF6 parton density function library')

    conflicts('+lhapdf5', when='+lhapdf6', msg="Choose LHAPDF5 or LHAPDF6")

    depends_on('gsl')
    depends_on('log4cpp')
    depends_on('libxml2')
    depends_on('pythia6')
    depends_on('root')
    depends_on('lhapdf5', when='+lhapdf5')
    depends_on('lhapdf6', when='+lhapdf6')

    def setup_environment(self, spack_env, run_env):
        if self.build_directory:
            spack_env.set('GENIE', self.build_directory)
        run_env.set('GENIE', self.spec.prefix)

    def setup_dependent_environment(self, spack_env, run_env, dependent_spec):
        spack_env.set('GENIE', self.spec.prefix)
        run_env.set('GENIE', self.spec.prefix)

    def configure_args(self):
        env['GENIE'] = self.build_directory

        spec = self.spec
        args = [
            '--with-pythia6-lib={}'.format(self.spec['pythia6'].prefix.lib),
            '--with-libxml2-inc={}'.format(self.spec['libxml2'].prefix.include),
            '--with-libxml2-lib={}'.format(self.spec['libxml2'].prefix.lib),
            '--with-log4cpp-inc={}'.format(self.spec['log4cpp'].prefix.include),
            '--with-log4cpp-lib={}'.format(self.spec['log4cpp'].prefix.lib),
        ]

        if '+lhapdf5' in spec:
            args.extend([
                '--enable-lhapdf5',
                '--with-lhapdf5-inc={}'.format(self.spec['lhapdf5'].prefix.include),
                '--with-lhapdf5-lib={}'.format(self.spec['lhapdf5'].prefix.lib),
            ])
        else:
            args.append('--disable-lhapdf5')

        if '+lhapdf6' in spec:
            args.extend([
                '--enable-lhapdf6',
                '--with-lhapdf6-inc={}'.format(self.spec['lhapdf6'].prefix.include),
                '--with-lhapdf6-lib={}'.format(self.spec['lhapdf6'].prefix.lib),
            ])
        else:
            args.append('--disable-lhapdf6')

        return args

#    @run_after('install')
#    def install_extra(self, *args, **kwargs):
#        ins = which('install')
#        ins('-D', 'src/make/Make.config', os.path.join(prefix, 'src/make/Make.config'))
