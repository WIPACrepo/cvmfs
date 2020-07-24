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
import os
import glob

class Sprng(MakefilePackage):
    """The Scalable Parallel Random Number Generators Library."""

    homepage = "http://www.sprng.org/sprng.html"
    url      = "http://www.sprng.org/Version2.0/sprng2.0b.tar.gz"

    version('2.0b', 'cf825f9333d07acdcaa599f29f281b8d')

    variant('pic', default=True, description='Build PIC libraries')

    parallel = False

    def edit(self, spec, prefix):
        filter_file(r'^([^#].*)', r'#\1', 'make.CHOICES')
        filter_file(r'#PLAT = INTEL', 'PLAT = INTEL', 'make.CHOICES')

        filter_file(r'^CC\s*=.*', 'CC = '+spack_cc,  'SRC/make.INTEL')
        filter_file(r'^F77\s*=.*', 'F77 = '+spack_f77, 'SRC/make.INTEL')
        filter_file(r'^FFXN\s*=.*', 'FFXN = -DAdd_', 'SRC/make.INTEL')
        if '+pic' in spec:
            filter_file(r'^CFLAGS\s*=', 'CFLAGS = -fPIC', 'SRC/make.INTEL')

    def install(self, spec, prefix):
        ins = which('install')
        ins('-D', 'libsprng.a', os.path.join(prefix.lib, 'libsprng.a'))
        for f in glob.glob('include/*.h'):
            ins('-D', '-m', '644', f, os.path.join(prefix.include, 'sprng', os.path.basename(f)))
