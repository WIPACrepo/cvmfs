# Copyright 2013-2018 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)


from spack import *
import platform


class Geant4(CMakePackage):
    """Geant4 is a toolkit for the simulation of the passage of particles
    through matter. Its areas of application include high energy, nuclear
    and accelerator physics, as well as studies in medical and space
    science."""

    homepage = "http://geant4.cern.ch/"
    url = "https://geant4-data.web.cern.ch/releases/geant4.10.01.p03.tar.gz"

    version('10.05.p01', sha256='f4a292220500fad17e0167ce3153e96e3410ecbe96284e572dc707f63523bdff')
    version('10.04', 'b84beeb756821d0c61f7c6c93a2b83de')
    version('10.03.p03', 'ccae9fd18e3908be78784dc207f2d73b')
    version('10.02.p03', '2b887e66f0d41174016160707662a77b')
    version('10.02.p02', '6aae1d0fc743b0edc358c5c8fbe48657')
    version('10.02.p01', 'b81f7082a15f6a34b720b6f15c6289cfe4ddbbbdcef0dc52719f71fac95f7f1c')
    version('10.01.p03', '4fb4175cc0dabcd517443fbdccd97439')

    variant('qt', default=False, description='Enable Qt support')
    variant('vecgeom', default=False, description='Enable vecgeom support')
    variant('cxx11', default=True, description='Enable CXX11 support')
    variant('cxx14', default=False, description='Enable CXX14 support')
    variant('cxx17', default=False, description='Enable CXX17 support')
    variant('opengl', default=False, description='Optional OpenGL support')
    variant('x11', default=False, description='Optional X11 support')
    variant('motif', default=False, description='Optional motif support')
    variant('threads', default=True, description='Build with multithreading')

    depends_on('cmake@3.5:', type='build')

    conflicts('+cxx17', when='+cxx11')
    conflicts('+cxx17', when='+cxx14')
    conflicts('+cxx14', when='+cxx11')
    conflicts('+cxx14', when='+cxx17')
    conflicts('+cxx11', when='+cxx14')
    conflicts('+cxx11', when='+cxx17')

    # C++11 support
    depends_on("clhep@2.4.1.0+cxx11~cxx14~cxx17", when="@10.05.p01+cxx11~cxx14~cxx17")
    depends_on("clhep@2.4.0.0+cxx11~cxx14~cxx17", when="@10.04+cxx11~cxx14~cxx17")
    depends_on("clhep@2.3.4.3+cxx11~cxx14~cxx17", when="@10.03.p03+cxx11~cxx14~cxx17")
    depends_on("clhep@2.3.1.1+cxx11~cxx14~cxx17", when="@10.02.p01+cxx11~cxx14~cxx17")
    depends_on("clhep@2.3.1.1+cxx11~cxx14~cxx17", when="@10.02.p01+cxx11~cxx14~cxx17")
    depends_on("clhep@2.2.0.4+cxx11~cxx14~cxx17", when="@10.01.p03+cxx11~cxx14~cxx17")

    # C++14 support
    depends_on("clhep@2.4.1.0~cxx11+cxx14~cxx17", when="@10.05.p01~cxx11+cxx14~cxx17")
    depends_on("clhep@2.4.0.0~cxx11+cxx14~cxx17", when="@10.04~cxx11+cxx14~cxx17")
    depends_on("clhep@2.3.4.3~cxx11+cxx14~cxx17", when="@10.03.p03~cxx11+cxx14~cxx17")
    depends_on("clhep@2.3.1.1~cxx11+cxx14~cxx17", when="@10.02.p02~cxx11+cxx14~cxx17")
    depends_on("clhep@2.3.1.1~cxx11+cxx14~cxx17", when="@10.02.p01~cxx11+cxx14~cxx17")
    depends_on("clhep@2.2.0.4~cxx11+cxx14~cxx17", when="@10.01.p03~cxx11+cxx14~cxx17")

    # C++17 support
    depends_on("clhep@2.4.1.0~cxx11~cxx14+cxx17", when="@10.05.p01~cxx11~cxx14+cxx17")
    depends_on("clhep@2.4.0.0~cxx11~cxx14+cxx17", when="@10.04~cxx11~cxx14+cxx17")
    depends_on("clhep@2.3.4.3~cxx11~cxx14+cxx17", when="@10.03.p03~cxx11~cxx14+cxx17")
    depends_on("clhep@2.3.1.1~cxx11~cxx14+cxx17", when="@10.02.p02~cxx11~cxx14+cxx17")
    depends_on("clhep@2.3.1.1~cxx11~cxx14+cxx17", when="@10.02.p01~cxx11~cxx14+cxx17")
    depends_on("clhep@2.2.0.4~cxx11~cxx14+cxx17", when="@10.01.p03~cxx11~cxx14+cxx17")

    depends_on("expat")
    depends_on("zlib")
    depends_on("xerces-c")
    depends_on("mesa", when='+opengl')
    depends_on("libx11", when='+x11')
    depends_on("libxmu", when='+x11')
    depends_on("motif", when='+motif')
    depends_on("vecgeom", when="+vecgeom")
    depends_on("qt@4.8:4.999", when="+qt")

    def cmake_args(self):
        spec = self.spec

        options = [
            '-DGEANT4_USE_GDML=ON',
            '-DGEANT4_USE_SYSTEM_CLHEP=ON',
            '-DGEANT4_USE_G3TOG4=ON',
            '-DGEANT4_INSTALL_DATA=ON',
            '-DGEANT4_BUILD_TLS_MODEL=global-dynamic',
            '-DGEANT4_USE_SYSTEM_EXPAT=ON',
            '-DGEANT4_USE_SYSTEM_ZLIB=ON',
            '-DXERCESC_ROOT_DIR:STRING=%s' %
            spec['xerces-c'].prefix, ]

        arch = platform.system().lower()
        if arch is not 'darwin':
            if "+x11" in spec and "+opengl" in spec:
                options.append('-DGEANT4_USE_OPENGL_X11=ON')
            if "+motif" in spec and "+opengl" in spec:
                options.append('-DGEANT4_USE_XM=ON')
            if "+x11" in spec:
                options.append('-DGEANT4_USE_RAYTRACER_X11=ON')

        if '+cxx11' in spec:
            options.append('-DGEANT4_BUILD_CXXSTD=c++11')
        if '+cxx14' in spec:
            options.append('-DGEANT4_BUILD_CXXSTD=c++14')
        if '+cxx17' in spec:
            options.append('-DGEANT4_BUILD_CXXSTD=c++17')

        if '+qt' in spec:
            options.append('-DGEANT4_USE_QT=ON')
            options.append(
                '-DQT_QMAKE_EXECUTABLE=%s' %
                spec['qt'].prefix.bin.qmake)

        if '+vecgeom' in spec:
            options.append('-DGEANT4_USE_USOLIDS=ON')
            options.append('-DUSolids_DIR=%s' % spec[
                'vecgeom'].prefix.lib.CMake.USolids)

        on_or_off = lambda opt: 'ON' if '+' + opt in spec else 'OFF'
        options.append('-DGEANT4_BUILD_MULTITHREADED=' + on_or_off('threads'))

        return options

    def url_for_version(self, version):
        """Handle Geant4's unusual version string."""
        return ("https://geant4-data.web.cern.ch/releases/geant4.%s.tar.gz" % version)
