# Copyright 2013-2018 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *


class GlobusToolkit(AutotoolsPackage):
    """The Globus Toolkit is an open source software toolkit used for building
       grids"""

    homepage = "http://toolkit.globus.org"
    url      = "http://downloads.globus.org/toolkit/gt6/stable/installers/src/globus_toolkit-6.0.1506371041.tar.gz"

    version("6.0.1558548600", sha256="59a938ad6b43305c1d7e212a350260822e8c3b0a8cfd4d9bb68ff619992677cc")
    version('6.0.1535473965', sha256='8f016a0d572a1a2fd4d9e3cf8e0a4d5b3f44adab9b4d905d7a09be368d63bfef')
    version('6.0.1506371041', 'e17146f68e03b3482aaea3874d4087a5')
    version('6.0.1493989444', '9e9298b61d045e65732e12c9727ceaa8')

    variant('gram5', default=True, description='Build gram5')
    variant('myproxy', default=True, description='Build myproxy')

    depends_on('openssl')

    def configure_args(self):
        spec = self.spec
        args = []

        if '~gram5' in spec:
            args.append('--disable-gram5')

        if '~myproxy' in spec:
            args.append('--disable-myproxy')

        return args