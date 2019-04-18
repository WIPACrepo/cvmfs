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

class GenieReweight(MakefilePackage):
    """GENIE Reweight"""

    homepage = "https://github.com/GENIE-MC/Reweight"
    url = 'https://github.com/GENIE-MC/Reweight/archive/R-1_00_00.tar.gz'

    version('1_00_02', sha256='0acfa5b59bebd8a18b3d17d2ff12511f3e0028efb927a615dfd3f9c88b872d81')
    version('1_00_00', sha256='198687f8dd31848ee931a3dd01d60cd7312c7c2db00007c631af64d3e2c9088d')

    #patch('compiler.patch', when='@1_00_00:')
    #patch('install.patch', when='@1_00_00:')

    depends_on('genie')
    depends_on('log4cpp')
    depends_on('root')
