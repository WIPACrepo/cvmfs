# Copyright 2013-2018 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *


class Wcslib(AutotoolsPackage):
    """WCSLIB a C implementation of the coordinate transformations
    defined in the FITS WCS papers."""

    homepage = "http://www.atnf.csiro.au/people/mcalabre/WCS/wcslib/"
    url      = "ftp://ftp.atnf.csiro.au/pub/software/wcslib/wcslib-5.18.tar.bz2"

    version('5.18', '67a78354be74eca4f17d3e0853d5685f')

    variant('cfitsio', default=False, description='Include CFITSIO support')
    variant('x',       default=False, description='Use the X Window System')

    depends_on('gmake', type='build')
    depends_on('flex@2.5.9:', type='build')
    depends_on('cfitsio', when='+cfitsio')
    depends_on('libx11', when='+x')
    depends_on('curl', when='@3.42:')

    def configure_args(self):
        spec = self.spec

        # TODO: Add PGPLOT package
        args = ['--without-pgplot']

        if '+cfitsio' in spec:
            args.extend([
                '--with-cfitsio',
                '--with-cfitsiolib={0}'.format(
                    spec['cfitsio'].libs.directories[0]),
                '--with-cfitsioinc={0}'.format(
                    spec['cfitsio'].headers.directories[0]),
            ])
        else:
            args.append('--without-cfitsio')

        #if self.version >= Version('3.42'):
        #    args.append('LIBS="-pthread -lcurl -lm"')

        if '+x' in spec:
            args.append('--with-x')
        else:
            args.append('--without-x')

        return args
