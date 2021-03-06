# Copyright 2013-2018 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)


from spack import *
import sys


class Root(CMakePackage):
    """ROOT is a data analysis framework."""

    homepage = "https://root.cern.ch"
    url      = "https://root.cern/download/root_v6.14.00.source.tar.gz"

    # ###################### Versions ##########################

    # Master branch
    version('master', git="https://github.com/root-project/root.git",
        branch='master')

    # Development versions
    version('6.13.08', '2b4546fc4b712ba1d672401bee07f5b3')

    # Production version
    version('6.14.04', '58d78513abdcba3f12f0c838d00987bb', preferred=True)

    # Old versions
    version('6.14.02', 'f27351828e2f28137eca3d5302ad0376')
    version('6.14.00', '3613c930589734531ac8995486d41af5')
    version('6.12.06', 'bef6535a5d0cdf471b550da45a10f605')
    version('6.10.08', '88532f68e9e14691f530c60b55beb698')
    version('6.09.02', '4188dfeafb72df339a3d688fe92f57ec')
    version('6.08.06', 'bcf0be2df31a317d25694ad2736df268')
    version('6.06.08', '6ef0fe9bd9f88f3ce8890e3651142ee4')
    version('6.06.06', '4308449892210c8d36e36924261fea26')
    version('6.06.04', '55a2f98dd4cea79c9c4e32407c2d6d17')
    version('6.06.02', 'e9b8b86838f65b0a78d8d02c66c2ec55')
    version('5.34.36', '6a1ad549b3b79b10bbb1f116b49067ee')

    if sys.platform == 'darwin':
        patch('math_uint.patch', when='@6.06.02')
        patch('root6-60606-mathmore.patch', when='@6.06.06')

    # ###################### Variants ##########################

    variant('avahi', default=False,
        description='Compile with avahi')
    variant('aqua', default=False,
        description='Enable Aqua interface')
    # No need for a specific variant: libafterimage is not provided by spack
    # By default always true, we get the builtin included in the source
    # variant('asimage', default=True,
    #    description='Enable image processing support')
    variant('davix', default=True,
        description='Compile with external Davix')
    variant('emacs', default=False,
        description='Enable Emacs support')
    variant('examples', default=True,
        description='Install examples')
    variant('fftw', default=False,
        description='Enable Fast Fourier Transform support')
    variant('fits', default=False,
        description='Enable support for images and data from FITS files')
    variant('fortran', default=False,
        description='Enable the Fortran components of ROOT')
    variant('graphviz', default=False,
        description='Enable graphviz support')
    variant('gdml', default=True,
        description='Enable GDML writer and reader')
    variant('gsl', default=True,
        description='Enable linking against shared libraries for GSL')
    variant('http', default=False,
        description='Enable HTTP server support')
    variant('jemalloc', default=False,
        description='Enable using the jemalloc allocator')
    variant('kerberos', default=False,
        description='Enable Kerberos support')
    variant('ldap', default=False,
        description='Enable LDAP support')
    variant('libcxx', default=False,
        description='Build using libc++')
    variant('math', default=True,
        description='Build the new libMathMore extended math library')
    variant('memstat', default=True,
        description='Enable a memory stats utility to detect memory leaks')
    # Minuit must not be installed as a dependency of root
    # otherwise it crashes with the internal minuit library
    variant('minuit', default=True,
        description='Automatically search for support libraries')
    # variant('mysql', default=False) - not supported by spack
    variant('odbc', default=False,
        description='Enable ODBC support')
    variant('opengl', default=True,
        description='Enable OpenGL support')
    # variant('oracle', default=False) - not supported by spack
    variant('postgres', default=False,
        description='Enable postgres support')
    variant('pythia6', default=False,
        description='Enable pythia6 support')
    variant('pythia8', default=False,
        description='Enable pythia8 support')
    variant('python', default=True,
        description='Enable Python ROOT bindings')
    variant('qt4', default=False,
        description='Enable Qt graphics backend')
    variant('r', default=False,
        description='Enable R ROOT bindings')
    variant('rpath', default=True,
        description='Enable RPATH')
    variant('rootfit', default=True,
        description='Build the libRooFit advanced fitting package')
    variant('root7', default=False,
        description='Enable ROOT 7 support')
    variant('shadow', default=False,
        description='Enable shadow password support')
    variant('sqlite', default=False,
        description='Enable SQLite support')
    variant('ssl', default=False,
        description='Enable SSL encryption support')
    variant('table', default=False,
        description='Build libTable contrib library')
    variant('tbb', default=True,
        description='TBB multi-threading support')
    variant('test', default=False,
        description='Enable test suit of ROOT with CTest')
    variant('threads', default=True,
        description='Enable using thread library')
    variant('tiff', default=True,
        description='Include Tiff support in image processing')
    variant('tmva', default=True,
        description='Build TMVA multi variate analysis library')
    variant('unuran', default=True,
        description='Use UNURAN for random number generation')
    variant('vc', default=False,
        description='Enable Vc for adding new types for SIMD programming')
    variant('vdt', default=True,
        description='Enable set of fast and vectorisable math functions')
    variant('x', default=True,
        description='Enable set of graphical options')
    # variant('xinetd', default=False,  - not supported by spack
    #    description='Enable a daemon process manager')
    variant('xml', default=True,
        description='Enable XML parser interface')
    variant('xrootd', default=False,
        description='Build xrootd file server and its client')

    # ################# Variants dependencies ##########################

    # Davix variant also requires openssl support
    depends_on('openssl', when='+davix')

    # If not x variant, then asimage,opengl,qt4 and tiff are not needed either
    # or: if ~x then ~asimage~opengl~qt4~tiff

    # ###################### Compiler variants ########################

    variant('cxxstd',
            default='11',
            values=('11', '14', '17'),
            multi=False,
            description='Use the specified C++ standard when building.')

    # ###################### Dependencies ##############################

    # minimum cmake version required
    depends_on('cmake@3.4.3:', type='build')
    depends_on('pkgconfig', type='build')

    depends_on('lz4',    when='@6.13.02:')
    depends_on('xxhash', when='@6.13.02:')
    depends_on('xz')
    depends_on('pcre')
    depends_on('freetype')
    depends_on('libpng')
    depends_on('ncurses')
    depends_on('zlib')

    # X-Graphics
    depends_on('libx11',  when="+x")
    depends_on('libxext', when="+x")
    depends_on('libxft',  when="+x")
    depends_on('libxpm',  when="+x")

    # OpenGL
    depends_on('ftgl',  when="+x+opengl")
    depends_on('glew',  when="+x+opengl")
    depends_on('gl',    when="+x+opengl")
    depends_on('glu',   when="+x+opengl")
    depends_on('gl2ps', when="+x+opengl")

    # Qt4
    depends_on('qt', when='+qt4')

    # TMVA
    depends_on('py-numpy', when='+tmva')

    # Asimage variant would need one of these two
    # For the moment, we use the libafterimage provided by the root sources
    # depends_on('libafterimage',    when='+asimage') - not supported
    # depends_on('afterstep@2.2.11', when='+asimage') - not supported

    # Optional dependencies
    depends_on('avahi',     when='+avahi')
    depends_on('davix',     when='+davix')
    depends_on('cfitsio',   when='+fits')
    depends_on('fftw',      when='+fftw')
    depends_on('graphviz',  when='+graphviz')
    depends_on('gsl',       when='+gsl')
    depends_on('http',      when='+http')
    depends_on('jemalloc',  when='+jemalloc')
    depends_on('kerberos',  when='+kerberos')
    depends_on('ldap',      when='+ldap')
    depends_on('libcxx',    when='+libcxx')
    # depends_on('mysql',    when='+mysql')  - not supported
    depends_on('odbc',      when='+odbc')
    # depends_on('oracle',   when='+oracle')
    depends_on('openssl',   when='+ssl')
    depends_on('postgresql', when='+postgres')
    depends_on('pythia6@6:6.999+root',  when='+pythia6')
    depends_on('pythia@8:8.999',  when='+pythia8')
    depends_on('python@2.7:',     when='+python', type=('build', 'run'))
    depends_on('r',         when='+r', type=('build', 'run'))
    depends_on('r-cpp',     when='+r', type=('build', 'run'))
    depends_on('r-inside',  when='+r', type=('build', 'run'))
    depends_on('shadow',    when='+shadow')
    depends_on('sqlite',    when='+sqlite')
    depends_on('tbb',       when='+tbb')
    depends_on('unuran',    when='+unuran')
    depends_on('vc',        when='+vc')
    depends_on('veccore',   when='+veccore')
    depends_on('vdt',       when='+vdt')
    depends_on('libxml2',   when='+xml')
    depends_on('xrootd',    when='+xrootd')
    # depends_on('hdfs') - supported (TODO)

    # Old dependencies

    # depends_on('binutils')
    # depends_on('gif')  - provided by builtin afterimage
    # depends_on('jpeg') - provided by builtin afterimage
    # depends_on('libice')
    # depends_on('libsm')
    # depends_on('libxml2+python')

    # Not supported
    # depends_on('monalisa')

    # Grid packages - not supported yet by Spack
    # depends_on('castor')
    # depends_on('chirp')
    # depends_on('dcap')
    # depends_on('gfal')
    # depends_on('ldap')
    # depends_on('rfio')

    # I was unable to build root with any Intel compiler
    # See https://sft.its.cern.ch/jira/browse/ROOT-7517
    conflicts('%intel')

    # Incompatible variants
    conflicts('+tmva', when='~gsl', msg="TVMA requires GSL")

    def cmake_args(self):

        spec = self.spec

        options = []

        # #################### Base Settings #######################

        # ROOT should not download its own dependencies
        options = [
            '-Dexplicitlink=ON',
            '-Dexceptions=ON',
            '-Dfail-on-missing=ON',
            '-Dshared=ON',
            '-Dsoversion=ON',
            '-Dbuiltin_llvm=ON',
            '-Dbuiltin_afterimage=ON',
            '-Dasimage:BOOL=ON',  # if afterimage is taken from builtin
            '-Dastiff:BOOL=ON',   # asimage and astiff must be ON too
            '-Dbuiltin_cfitsio=OFF',
            '-Dbuiltin_davix=OFF',
            '-Dbuiltin_fftw3=OFF',
            '-Dbuiltin_freetype=OFF',
            '-Dbuiltin_ftgl=ON',
            '-Dbuiltin_gl2ps=OFF',
            '-Dbuiltin_glew=OFF',
            '-Dbuiltin_gsl=OFF',
            '-Dbuiltin_lzma=OFF',
            '-Dbuiltin_openssl=OFF',
            '-Dbuiltin_pcre=OFF',
            '-Dbuiltin_tbb=OFF',
            '-Dbuiltin_unuran=OFF',
            '-Dbuiltin_vc=OFF',
            '-Dbuiltin_vdt=OFF',
            '-Dbuiltin_veccore=OFF',
            '-Dbuiltin_xrootd=OFF',
            '-Dbuiltin_zlib=OFF'
        ]

        # LZ4 and xxhash do not work as external deps for older versions
        options.extend([
            '-Dbuiltin_lz4:BOOL=%s' % (
                'ON' if self.spec.satisfies('@:6.12.99') else 'OFF'),
            '-Dbuiltin_xxhash:BOOL=%s' % (
                'ON' if self.spec.satisfies('@:6.12.99') else 'OFF'),
        ])

        # #################### ROOT options #######################

        options.extend([
            '-Dx11:BOOL=%s' % (
                'ON' if '+x' in spec else 'OFF'),
            '-Dxft:BOOL=%s' % (
                'ON' if '+x' in spec else 'OFF'),
            '-Dbonjour:BOOL=%s' % (
                'ON' if '+avahi' in spec else 'OFF'),
            '-Dcocoa:BOOL=%s' % (
                'ON' if '+aqua' in spec else 'OFF'),
            '-Dcxx14:BOOL=%s' % (
                'ON' if '+root7' in spec else 'OFF'),
            # -Dcxxmodules=OFF # use clang C++ modules
            '-Ddavix:BOOL=%s' % (
                'ON' if '+davix' in spec else 'OFF'),
            '-Dfftw3:BOOL=%s' % (
                'ON' if '+fftw' in spec else 'OFF'),
            '-Dfitsio:BOOL=%s' % (
                'ON' if '+fits' in spec else 'OFF'),
            '-Dfortran:BOOL=%s' % (
                'ON' if '+fortran' in spec else 'OFF'),
            '-Dftgl:BOOL=%s' % (
                'ON' if '+opengl' in spec else 'OFF'),
            '-Dgdml:BOOL=%s' % (
                'ON' if '+gdml' in spec else 'OFF'),
            '-Dgl2ps:BOOL=%s' % (
                'ON' if '+opengl' in spec else 'OFF'),
            '-Dgenvector:BOOL=%s' % (
                'ON' if '+math' in spec else 'OFF'),  # default ON
            '-Dgsl_shared:BOOL=%s' % (
                'ON' if '+gsl' in spec else 'OFF'),
            '-Dgviz:BOOL=%s' % (
                'ON' if '+graphviz' in spec else 'OFF'),
            '-Dhttp:BOOL=%s' % (
                'ON' if '+http' in spec else 'OFF'),
            '-Dimt:BOOL=%s' % (
                'ON' if '+tbb' in spec else 'OFF'),
            '-Djemalloc:BOOL=%s' % (
                'ON' if '+jemalloc' in spec else 'OFF'),
            '-Dkrb5:BOOL=%s' % (
                'ON' if '+kerberos' in spec else 'OFF'),
            '-Dldap:BOOL=%s' % (
                'ON' if '+ldap' in spec else 'OFF'),
            '-Dlibcxx:BOOL=%s' % (
                'ON' if '+libcxx' in spec else 'OFF'),
            '-Dmathmore:BOOL=%s' % (
                'ON' if '+math' in spec else 'OFF'),
            '-Dmemstat:BOOL=%s' % (
                'ON' if '+memstat' in spec else 'OFF'),
            '-Dminimal:BOOL=%s' % (
                'ON' if '+minimal' in spec else 'OFF'),
            '-Dminuit:BOOL=%s' % (
                'ON' if '+minuit' in spec else 'OFF'),
            '-Dminuit2:BOOL=%s' % (
                'ON' if '+minuit' in spec else 'OFF'),
            '-Dmysql:BOOL=%s' % (
                'ON' if '+mysql' in spec else 'OFF'),  # not supported
            '-Dodbc:BOOL=%s' % (
                'ON' if '+odbc' in spec else 'OFF'),
            '-Dopengl:BOOL=%s' % (
                'ON' if '+opengl' in spec else 'OFF'),
            '-Doracle:BOOL=%s' % (
                'ON' if '+oracle' in spec else 'OFF'),  # not supported
            '-Dpch:BOOL=%s' % (
                'ON' if '+pch' in spec else 'OFF'),  # needs cling
            '-Dpgsql:BOOL=%s' % (
                'ON' if '+postgres' in spec else 'OFF'),
            '-Dpythia6:BOOL=%s' % (
                'ON' if '+pythia6' in spec else 'OFF'),
            '-Dpythia8:BOOL=%s' % (
                'ON' if '+pythia8' in spec else 'OFF'),
            '-Dpython:BOOL=%s' % (
                'ON' if '+python' in spec else 'OFF'),
            '-Dqt:BOOL=%s' % (
                'ON' if '+qt4' in spec else 'OFF'),
            '-Dqtgsi:BOOL=%s' % (
                'ON' if '+qt4' in spec else 'OFF'),
            '-Dr:BOOL=%s' % (
                'ON' if '+R' in spec else 'OFF'),
            '-Droofit:BOOL=%s' % (
                'ON' if '+roofit' in spec else 'OFF'),
            '-Droot7:BOOL=%s' % (
                'ON' if '+root7' in spec else 'OFF'),  # requires C++14
            '-Drpath:BOOL=%s' % (
                'ON' if '+rpath' in spec else 'OFF'),
            '-Dshadowpw:BOOL=%s' % (
                'ON' if '+shadow' in spec else 'OFF'),
            '-Dsqlite:BOOL=%s' % (
                'ON' if '+sqlite' in spec else 'OFF'),
            '-Dssl:BOOL=%s' % (
                'ON' if '+ssl' in spec else 'OFF'),
            '-Dtable:BOOL=%s' % (
                'ON' if '+table' in spec else 'OFF'),
            '-Dtbb:BOOL=%s' % (
                'ON' if '+tbb' in spec else 'OFF'),
            '-Dtesting:BOOL=%s' % (
                'ON' if '+test' in spec else 'OFF'),
            '-Dthread:BOOL=%s' % (
                'ON' if '+threads' in spec else 'OFF'),
            '-Dtmva:BOOL=%s' % (
                'ON' if '+tmva' in spec else 'OFF'),
            '-Dunuran:BOOL=%s' % (
                'ON' if '+unuran' in spec else 'OFF'),
            '-Dvc:BOOL=%s' % (
                'ON' if '+vc' in spec else 'OFF'),
            '-Dveccore:BOOL=%s' % (
                 'ON' if '+veccore' in spec else 'OFF'),  # not supported
            '-Dvdt:BOOL=%s' % (
                'ON' if '+vdt' in spec else 'OFF'),
            '-Dxml:BOOL=%s' % (
                'ON' if '+xml' in spec else 'OFF'),  # default ON
            '-Dxrootd:BOOL=%s' % (
                'ON' if '+xrootd' in spec else 'OFF'),  # default ON

            # Fixed options
            '-Dafdsmrgd=OFF',  # not supported
            '-Dafs=OFF',      # not supported
            '-Dalien=OFF',
            '-Dcastor=OFF',   # not supported
            '-Dccache=OFF',   # not supported
            '-Dchirp=OFF',
            '-Dcling=ON',
            '-Ddcache=OFF',  # not supported
            '-Dgeocad=OFF',  # not supported
            '-Dgfal=OFF',    # not supported
            '-Dglite=OFF',   # not supported
            '-Dglobus=OFF',
            '-Dgminimal=OFF',
            '-Dgnuinstall=OFF',
            '-Dhdfs=OFF',    # TODO pending to add
            '-Dmonalisa=OFF',  # not supported
            '-Drfio=OFF',      # not supported
            '-Droottest=OFF',  # requires network
            '-Druby=OFF',      # unmantained upstream
            '-Druntime_cxxmodules=OFF',  # use clang C++ modules, experimental
            '-Dsapdb=OFF',     # option not implemented
            '-Dsrp=OFF',       # option not implemented
            '-Dtcmalloc=OFF'

        ])

        # #################### Compiler options ####################

        if sys.platform == 'darwin':
            if self.compiler.cc == 'gcc':
                options.extend([
                    '-DCMAKE_C_FLAGS=-D__builtin_unreachable=__builtin_trap',
                    '-DCMAKE_CXX_FLAGS=-D__builtin_unreachable=__builtin_trap',
                ])

        options.append(
            '-Dcxx{0}=ON'.format(self.spec.variants['cxxstd'].value)
        )

        return options

    def setup_environment(self, spack_env, run_env):
        run_env.prepend_path('PYTHONPATH', self.prefix.lib)

    def setup_dependent_environment(self, spack_env, run_env, dependent_spec):
        spack_env.set('ROOTSYS', self.prefix)
        spack_env.set('ROOT_VERSION', 'v{0}'.format(self.version.up_to(1)))
        spack_env.prepend_path('PYTHONPATH', self.prefix.lib)
