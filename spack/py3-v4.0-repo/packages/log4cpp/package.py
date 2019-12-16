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


class Log4cpp(AutotoolsPackage):
    """A library of C++ classes for flexible logging to files (rolling),
       syslog, IDSA and other destinations. It is modeled after the Log
       for Java library (http://www.log4j.org), staying as close to their
       API as is reasonable."""

    homepage = "https://sourceforge.net/projects/log4cpp/"
    url      = "http://downloads.sourceforge.net/project/log4cpp/log4cpp-1.1.x (new)/log4cpp-1.1/log4cpp-1.1.3.tar.gz"

    def url_for_version(self, version):
        url = "http://versaweb.dl.sourceforge.net/project/log4cpp/log4cpp-1.1.x (new)/log4cpp-1.1/log4cpp-{0}.tar.gz"
        return url.format(version)

    version('1.1.3', 'b9e2cee932da987212f2c74b767b4d8b')
    version('1.1.2', 'c70eac7334e2f3cbeac307dc78532be4')
    version('1.1.1', '1e173df8ee97205f412ff84aa93b8fbe')
    version('1.1',   'b9ef6244baa5e5e435f35e0b9474b35d')

    variant('shared', default=True, description='Build shared libraries')
    variant('static', default=True, description='Build static libraries')

    # depends_on('foo')

    def configure_args(self):
        args = []
        spec = self.spec

        if '+shared' in spec:
            args.append('--enable-shared')
        else:
            args.append('--disable-shared')

        if '+static' in spec:
            args.append('--enable-static')
        else:
            args.append('--disable-static')

        return args
