"""pythia6 build/install"""

import os
import subprocess
import tempfile
import shutil
from glob import glob

from build_util import wget, unpack, version_dict, get_fortran_compiler, cpu_cores

cmakelists = """
# ======================================================================
#  pythia6 main build file
#
#  setup cmake
#  cd .../path/to/build/directory
#  cmake [-DCMAKE_INSTALL_PREFIX=/install/path]
#        [-DCMAKE_BUILD_TYPE=<RelWithDebInfo|Debug|Release|MinSizeRel> ]
#        [-Drun_long_tests:BOOL=ON]
#        .../path/to/pythia/source
#  make
#  make test
#  make install
# ======================================================================

# use cmake 2.6 or later
cmake_minimum_required (VERSION 2.6)

project(pythia6 C Fortran)
message(STATUS "pythia version is ${PYTHIA6_VERSION}")

enable_testing()

#build all libraries in a single directory to enable testing
set(LIBRARY_OUTPUT_PATH ${PROJECT_BINARY_DIR}/lib)

# set compiler flags
# default GNU compiler flags:
# DEBUG           -g
# RELEASE         -O3 -DNDEBUG
# MINSIZEREL      -Os -DNDEBUG
# RELWITHDEBINFO  -O2 -g
set( CMAKE_C_FLAGS_DEBUG "-g -O0 -m64 -fPIC" )
set( CMAKE_C_FLAGS_RELWITHDEBINFO "-O3 -g -DNDEBUG -fno-omit-frame-pointer -m64 -fPIC" )
set( CMAKE_C_FLAGS_RELEASE "-O3 -DNDEBUG -m64 -fPIC" )
set( CMAKE_Fortran_FLAGS_DEBUG "-g -O0 -fno-second-underscore -m64 -fPIC" )
set( CMAKE_Fortran_FLAGS_RELWITHDEBINFO "-O3 -g -DNDEBUG -fno-omit-frame-pointer -fno-second-underscore -m64 -fPIC" )
set( CMAKE_Fortran_FLAGS_RELEASE "-O3 -DNDEBUG -fno-second-underscore -m64 -fPIC" )

message(STATUS "CMAKE_Fortran_COMPILER_INIT = ${CMAKE_Fortran_COMPILER_INIT}")
message(STATUS "CMAKE_Fortran_COMPILER_FULLPATH = ${CMAKE_Fortran_COMPILER_FULLPATH}")
message(STATUS "CMAKE_Fortran_COMPILER = ${CMAKE_Fortran_COMPILER}")

if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE RelWithDebInfo CACHE STRING "" FORCE)
endif()
message(STATUS "cmake build type set to ${CMAKE_BUILD_TYPE}")

message("ENV_FLAGS = $ENV{FFLAGS}")
string(TOUPPER ${CMAKE_BUILD_TYPE} BTYPE_UC )
if( ${BTYPE_UC} MATCHES "DEBUG")
  set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS_DEBUG}")
  set(CMAKE_Fortran_FLAGS "${CMAKE_Fortran_FLAGS_DEBUG}")
elseif( ${BTYPE_UC} MATCHES "RELEASE")
  set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS_RELEASE}")
  set(CMAKE_Fortran_FLAGS "${CMAKE_Fortran_FLAGS_RELEASE}")
elseif( ${BTYPE_UC} MATCHES "RELWITHDEBINFO")
  set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS_RELWITHDEBINFO}")
  set(CMAKE_Fortran_FLAGS "${CMAKE_Fortran_FLAGS_RELWITHDEBINFO}")
endif()
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} $ENV{CFLAGS}")
set(CMAKE_Fortran_FLAGS "${CMAKE_Fortran_FLAGS} $ENV{FFLAGS}")
message("CMAKE_C_FLAGS = ${CMAKE_C_FLAGS}")
message("CMAKE_Fortran_FLAGS = ${CMAKE_Fortran_FLAGS}")

# source
# shared library
file(GLOB src_files *.c *.F *.f)
add_library(Pythia6 SHARED ${src_files})

# Installation:
# Library.
install(TARGETS Pythia6 DESTINATION lib)

# Include-able file.
#install( FILES example/main60.f
#         DESTINATION include )

# Documentation.
#install(DIRECTORY doc DESTINATION .)

# Examples
#install(DIRECTORY example DESTINATION .)

# tests
#macro( pythia_test testname )
#  set ( package_library_list ${PROJECT_BINARY_DIR}/lib/${CMAKE_STATIC_LIBRARY_PREFIX}CLHEP-${PACKAGE}-${VERSION}${CMAKE_STATIC_LIBRARY_SUFFIX} )
#  link_libraries( Pythia6 )
#  message( STATUS "building ${testname} from ${CMAKE_CURRENT_SOURCE_DIR}/example in ${CMAKE_CURRENT_BINARY_DIR}" )
#  add_executable(${testname} example/${testname}.f)
#  add_test( ${testname} ${CMAKE_CURRENT_BINARY_DIR}/${testname} )
#endmacro( pythia_test )
#
#pythia_test( main61 )
#pythia_test( main63 )
#pythia_test( main66 )
#pythia_test( main67 )
#pythia_test( main68 )
#pythia_test( main69 )
#pythia_test( main71 )
#pythia_test( main72 )
#pythia_test( main73 )
#pythia_test( main75 )
#pythia_test( main77 )
#pythia_test( main78 )
#pythia_test( main81 )

# these examples take a while to run
#if( run_long_tests )
#  pythia_test( main62 )
#  pythia_test( main64 )
#  pythia_test( main65 )
#  pythia_test( main70 )
#  pythia_test( main74 )
#  pythia_test( main79 )
#endif( run_long_tests )
"""

pythia6_patch = """
diff -Naur pytime.f pytime.f
--- pytime.f	2018-08-23 11:24:27.000000000 -0500
+++ pytime.f	2018-08-23 11:46:08.189999826 -0500
@@ -1,4 +1,3 @@
- 
 C*********************************************************************
  
 C...PYTIME
@@ -59,17 +58,18 @@
 C      IDATI(6)=ISEC
  
 C...Example 4: GNU LINUX libU77, SunOS.
-C      CALL IDATE(IDTEMP)
-C      IDATI(1)=IDTEMP(3)
-C      IDATI(2)=IDTEMP(2)
-C      IDATI(3)=IDTEMP(1)
-C      CALL ITIME(IDTEMP)
-C      IDATI(4)=IDTEMP(1)
-C      IDATI(5)=IDTEMP(2)
-C      IDATI(6)=IDTEMP(3)
+      CALL IDATE(IDTEMP)
+      IDATI(1)=IDTEMP(3)
+      IDATI(2)=IDTEMP(2)
+      IDATI(3)=IDTEMP(1)
+      CALL ITIME(IDTEMP)
+      IDATI(4)=IDTEMP(1)
+      IDATI(5)=IDTEMP(2)
+      IDATI(6)=IDTEMP(3)
  
 C...Common code to ensure right century.
       IDATI(1)=2000+MOD(IDATI(1),100)
  
       RETURN
       END
+ 
diff -Naur upevnt.f upevnt.f
--- upevnt.f	2018-08-23 11:24:27.000000000 -0500
+++ upevnt.f	2018-08-23 11:46:08.189999826 -0500
@@ -1,56 +1,3 @@
-
-C...Old example: handles a simple Pythia 6.4 initialization file.
- 
-c      SUBROUTINE UPINIT
- 
-C...Double precision and integer declarations.
-c      IMPLICIT DOUBLE PRECISION(A-H, O-Z)
-c      IMPLICIT INTEGER(I-N)
- 
-C...Commonblocks.
-c      COMMON/PYDAT1/MSTU(200),PARU(200),MSTJ(200),PARJ(200)
-c      COMMON/PYPARS/MSTP(200),PARP(200),MSTI(200),PARI(200)
-c      SAVE /PYDAT1/,/PYPARS/
- 
-C...User process initialization commonblock.
-c      INTEGER MAXPUP
-c      PARAMETER (MAXPUP=100)
-c      INTEGER IDBMUP,PDFGUP,PDFSUP,IDWTUP,NPRUP,LPRUP
-c      DOUBLE PRECISION EBMUP,XSECUP,XERRUP,XMAXUP
-c      COMMON/HEPRUP/IDBMUP(2),EBMUP(2),PDFGUP(2),PDFSUP(2),
-c     &IDWTUP,NPRUP,XSECUP(MAXPUP),XERRUP(MAXPUP),XMAXUP(MAXPUP),
-c     &LPRUP(MAXPUP)
-c      SAVE /HEPRUP/
- 
-C...Read info from file.
-c      IF(MSTP(161).GT.0) THEN
-c        READ(MSTP(161),*,END=110,ERR=110) IDBMUP(1),IDBMUP(2),EBMUP(1),
-c     &  EBMUP(2),PDFGUP(1),PDFGUP(2),PDFSUP(1),PDFSUP(2),IDWTUP,NPRUP
-c        DO 100 IPR=1,NPRUP
-c          READ(MSTP(161),*,END=110,ERR=110) XSECUP(IPR),XERRUP(IPR),
-c     &    XMAXUP(IPR),LPRUP(IPR)
-c  100   CONTINUE
-c        RETURN
-C...Error or prematurely reached end of file.
-c  110   WRITE(MSTU(11),5000)
-c        STOP
- 
-C...Else not implemented.
-c      ELSE
-c        WRITE(MSTU(11),5100)
-c        STOP
-c      ENDIF
- 
-C...Format for error printout.
-c 5000 FORMAT(1X,'Error: UPINIT routine failed to read information'/
-c     &1X,'Execution stopped!')
-c 5100 FORMAT(1X,'Error: You have not implemented UPINIT routine'/
-c     &1X,'Dummy routine in PYTHIA file called instead.'/
-c     &1X,'Execution stopped!')
- 
-c      RETURN
-c      END
- 
 C*********************************************************************
  
 C...UPEVNT
@@ -120,3 +67,54 @@
  
       RETURN
       END
+
+C...Old example: handles a simple Pythia 6.4 event file.
+ 
+c      SUBROUTINE UPEVNT
+ 
+C...Double precision and integer declarations.
+c      IMPLICIT DOUBLE PRECISION(A-H, O-Z)
+c      IMPLICIT INTEGER(I-N)
+ 
+C...Commonblocks.
+c      COMMON/PYDAT1/MSTU(200),PARU(200),MSTJ(200),PARJ(200)
+c      COMMON/PYPARS/MSTP(200),PARP(200),MSTI(200),PARI(200)
+c      SAVE /PYDAT1/,/PYPARS/
+ 
+C...User process event common block.
+c      INTEGER MAXNUP
+c      PARAMETER (MAXNUP=500)
+c      INTEGER NUP,IDPRUP,IDUP,ISTUP,MOTHUP,ICOLUP
+c      DOUBLE PRECISION XWGTUP,SCALUP,AQEDUP,AQCDUP,PUP,VTIMUP,SPINUP
+c      COMMON/HEPEUP/NUP,IDPRUP,XWGTUP,SCALUP,AQEDUP,AQCDUP,IDUP(MAXNUP),
+c     &ISTUP(MAXNUP),MOTHUP(2,MAXNUP),ICOLUP(2,MAXNUP),PUP(5,MAXNUP),
+c     &VTIMUP(MAXNUP),SPINUP(MAXNUP)
+c      SAVE /HEPEUP/
+ 
+C...Read info from file.
+c      IF(MSTP(162).GT.0) THEN
+c        READ(MSTP(162),*,END=110,ERR=110) NUP,IDPRUP,XWGTUP,SCALUP,
+c     &  AQEDUP,AQCDUP
+c        DO 100 I=1,NUP
+c          READ(MSTP(162),*,END=110,ERR=110) IDUP(I),ISTUP(I),
+c     &    MOTHUP(1,I),MOTHUP(2,I),ICOLUP(1,I),ICOLUP(2,I),
+c     &    (PUP(J,I),J=1,5),VTIMUP(I),SPINUP(I)
+c  100   CONTINUE
+c        RETURN
+C...Special when reached end of file or other error.
+c  110   NUP=0
+ 
+C...Else not implemented.
+c      ELSE
+c        WRITE(MSTU(11),5000)
+c        STOP
+c      ENDIF
+ 
+C...Format for error printout.
+c 5000 FORMAT(1X,'Error: You have not implemented UPEVNT routine'/
+c     &1X,'Dummy routine in PYTHIA file called instead.'/
+c     &1X,'Execution stopped!')
+ 
+c      RETURN
+c      END
+ 
diff -Naur upinit.f upinit.f
--- upinit.f	2018-08-23 11:24:27.000000000 -0500
+++ upinit.f	2018-08-23 11:46:08.190999819 -0500
@@ -1,4 +1,3 @@
- 
 C*********************************************************************
  
 C...UPINIT
@@ -64,3 +63,56 @@
  
       RETURN
       END
+
+C...Old example: handles a simple Pythia 6.4 initialization file.
+ 
+c      SUBROUTINE UPINIT
+ 
+C...Double precision and integer declarations.
+c      IMPLICIT DOUBLE PRECISION(A-H, O-Z)
+c      IMPLICIT INTEGER(I-N)
+ 
+C...Commonblocks.
+c      COMMON/PYDAT1/MSTU(200),PARU(200),MSTJ(200),PARJ(200)
+c      COMMON/PYPARS/MSTP(200),PARP(200),MSTI(200),PARI(200)
+c      SAVE /PYDAT1/,/PYPARS/
+ 
+C...User process initialization commonblock.
+c      INTEGER MAXPUP
+c      PARAMETER (MAXPUP=100)
+c      INTEGER IDBMUP,PDFGUP,PDFSUP,IDWTUP,NPRUP,LPRUP
+c      DOUBLE PRECISION EBMUP,XSECUP,XERRUP,XMAXUP
+c      COMMON/HEPRUP/IDBMUP(2),EBMUP(2),PDFGUP(2),PDFSUP(2),
+c     &IDWTUP,NPRUP,XSECUP(MAXPUP),XERRUP(MAXPUP),XMAXUP(MAXPUP),
+c     &LPRUP(MAXPUP)
+c      SAVE /HEPRUP/
+ 
+C...Read info from file.
+c      IF(MSTP(161).GT.0) THEN
+c        READ(MSTP(161),*,END=110,ERR=110) IDBMUP(1),IDBMUP(2),EBMUP(1),
+c     &  EBMUP(2),PDFGUP(1),PDFGUP(2),PDFSUP(1),PDFSUP(2),IDWTUP,NPRUP
+c        DO 100 IPR=1,NPRUP
+c          READ(MSTP(161),*,END=110,ERR=110) XSECUP(IPR),XERRUP(IPR),
+c     &    XMAXUP(IPR),LPRUP(IPR)
+c  100   CONTINUE
+c        RETURN
+C...Error or prematurely reached end of file.
+c  110   WRITE(MSTU(11),5000)
+c        STOP
+ 
+C...Else not implemented.
+c      ELSE
+c        WRITE(MSTU(11),5100)
+c        STOP
+c      ENDIF
+ 
+C...Format for error printout.
+c 5000 FORMAT(1X,'Error: UPINIT routine failed to read information'/
+c     &1X,'Execution stopped!')
+c 5100 FORMAT(1X,'Error: You have not implemented UPINIT routine'/
+c     &1X,'Dummy routine in PYTHIA file called instead.'/
+c     &1X,'Execution stopped!')
+ 
+c      RETURN
+c      END
+ 
diff -Naur upveto.f upveto.f
--- upveto.f	2018-08-23 11:24:27.000000000 -0500
+++ upveto.f	2018-08-23 11:46:08.190999819 -0500
@@ -1,54 +1,3 @@
-
-C...Old example: handles a simple Pythia 6.4 event file.
- 
-c      SUBROUTINE UPEVNT
- 
-C...Double precision and integer declarations.
-c      IMPLICIT DOUBLE PRECISION(A-H, O-Z)
-c      IMPLICIT INTEGER(I-N)
- 
-C...Commonblocks.
-c      COMMON/PYDAT1/MSTU(200),PARU(200),MSTJ(200),PARJ(200)
-c      COMMON/PYPARS/MSTP(200),PARP(200),MSTI(200),PARI(200)
-c      SAVE /PYDAT1/,/PYPARS/
- 
-C...User process event common block.
-c      INTEGER MAXNUP
-c      PARAMETER (MAXNUP=500)
-c      INTEGER NUP,IDPRUP,IDUP,ISTUP,MOTHUP,ICOLUP
-c      DOUBLE PRECISION XWGTUP,SCALUP,AQEDUP,AQCDUP,PUP,VTIMUP,SPINUP
-c      COMMON/HEPEUP/NUP,IDPRUP,XWGTUP,SCALUP,AQEDUP,AQCDUP,IDUP(MAXNUP),
-c     &ISTUP(MAXNUP),MOTHUP(2,MAXNUP),ICOLUP(2,MAXNUP),PUP(5,MAXNUP),
-c     &VTIMUP(MAXNUP),SPINUP(MAXNUP)
-c      SAVE /HEPEUP/
- 
-C...Read info from file.
-c      IF(MSTP(162).GT.0) THEN
-c        READ(MSTP(162),*,END=110,ERR=110) NUP,IDPRUP,XWGTUP,SCALUP,
-c     &  AQEDUP,AQCDUP
-c        DO 100 I=1,NUP
-c          READ(MSTP(162),*,END=110,ERR=110) IDUP(I),ISTUP(I),
-c     &    MOTHUP(1,I),MOTHUP(2,I),ICOLUP(1,I),ICOLUP(2,I),
-c     &    (PUP(J,I),J=1,5),VTIMUP(I),SPINUP(I)
-c  100   CONTINUE
-c        RETURN
-C...Special when reached end of file or other error.
-c  110   NUP=0
- 
-C...Else not implemented.
-c      ELSE
-c        WRITE(MSTU(11),5000)
-c        STOP
-c      ENDIF
- 
-C...Format for error printout.
-c 5000 FORMAT(1X,'Error: You have not implemented UPEVNT routine'/
-c     &1X,'Dummy routine in PYTHIA file called instead.'/
-c     &1X,'Execution stopped!')
- 
-c      RETURN
-c      END
- 
 C*********************************************************************
  
 C...UPVETO
@@ -98,3 +47,4 @@
  
       RETURN
       END
+ 
"""

def install(dir_name,version=None):
    if not os.path.exists(os.path.join(dir_name,'lib','libPythia6.so')):
        print('installing pythia6 version',version)
        name = 'pythia-'+version+'.tgz'
        try:
            tmp_dir = tempfile.mkdtemp()
            root_name = 'pythia6'
            root_path = os.path.join(tmp_dir,'pythia6.tar.gz')
            root_url = 'https://root.cern.ch/download/pythia6.tar.gz'
            wget(root_url,root_path)
            unpack(root_path,tmp_dir)
            root_dir = os.path.join(tmp_dir,root_name)

            path = os.path.join(tmp_dir,name)
            url = os.path.join('http://www.hepforge.org/archive/pythiasix/',name)
            wget(url,path)
            build_dir = os.path.join(tmp_dir,'pythia-'+version)
            os.mkdir(build_dir)
            unpack(path,build_dir)
            
            placement = {
                'pythia6_common_address.c': 'pythia6_common_address.c',
                'tpythia6_called_from_cc.F': 'tpythia6_called_from_cc.F'
            }
            for src,dest in placement.items():
                shutil.copy2(os.path.join(root_dir,src), os.path.join(build_dir,dest))

            with open(os.path.join(build_dir,'CMakeLists.txt'), 'w') as f:
                f.write(cmakelists)
            with open(os.path.join(tmp_dir,'pythia6_patch'), 'w') as f:
                f.write(pythia6_patch)
            if subprocess.call("patch -p0 <"+os.path.join(tmp_dir,'pythia6_patch'),cwd=build_dir,shell=True):
                raise Exception('pythia6 install could not be patched')

            cmake_dir = os.path.join(tmp_dir,'build')
            os.mkdir(cmake_dir)

            mod_env = dict(os.environ)
            mod_env['FC'] = get_fortran_compiler()
            if subprocess.call(['cmake', '-DCMAKE_INSTALL_PREFIX={}'.format(dir_name),
                                '-DPYTHIA6_VERSION={}'.format(version), build_dir],
                               cwd=cmake_dir, env=mod_env):
                raise Exception('pythia6 failed to cmake')
            if subprocess.call(['make','-j',cpu_cores], cwd=cmake_dir, env=mod_env):
                raise Exception('pythia6 failed to make')
            if subprocess.call(['make','install'], cwd=cmake_dir, env=mod_env):
                raise Exception('pythia6 failed to install')
        finally:
            shutil.rmtree(tmp_dir)

def versions():
    return version_dict(install)
