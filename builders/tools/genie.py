"""genie build/install"""

import os
import subprocess
import tempfile
import shutil

from build_util import wget, unpack, version_dict

# patch the makefile to actually use the compiler we give it
compiler_patch = """
--- a/src/make/Make.include
+++ b/src/make/Make.include
@@ -267,21 +267,8 @@ RANLIB    = ranlib
 #                        COMPILER OPTIONS
 #-------------------------------------------------------------------
 
-ifeq ($(GOPT_WITH_COMPILER),$(filter $(GOPT_WITH_COMPILER),clang clang++))
-  # --clang
-  CXX           = clang++
-  CC            = clang
-  LD            = clang++
-else
-  ifeq ($(GOPT_WITH_COMPILER),$(filter $(GOPT_WITH_COMPILER),gcc g++))
-    # -- gcc
-    CXX = g++
-    CC  = gcc
-    LD  = g++
-  else
-    $(error GOPT_WITH_COMPILER not set correctly!)
-  endif
-endif
+LD=$(CXX)
+
 #check if we're using clang (complicated because g++ is sometimes a clang alias...)
 APPLE_CLANG := $(shell $(CXX) -v 2>&1 | sed -n "s/.*clang//p" | cut -d . -f 1)
 ifneq ($(APPLE_CLANG),)
"""

# patch the makefile to install things correctly
install_patch = """
--- a/Makefile
+++ b/Makefile
@@ -417,7 +417,7 @@
 	cd Utils &&                  $(MAKE) install && cd .. && \\
 	cd VLE &&                    $(MAKE) install && cd .. && \\
 	cd VHE &&                    $(MAKE) install && cd .. && \\
-	cd ${GENIE}
+	install -D ${GENIE}/src/make/Make.config_no_paths ${GENIE_INSTALLATION_PATH}/src/make/Make.config_no_paths
 
 purge: FORCE
 	@echo " "
"""


def install(dir_name,version=None,data_dir=None):
    if not os.path.exists(os.path.join(dir_name,'bin','genie')):
        print('installing genie version',version)
        name = 'R-{}.tar.gz'.format(version)
        base_url = 'https://github.com/GENIE-MC/Generator/archive'
        try:
            tmp_dir = tempfile.mkdtemp()
            path = os.path.join(tmp_dir,name)
            url = os.path.join(base_url,name)
            wget(url,path)
            unpack(path,tmp_dir)
            genie_dir = os.path.join(tmp_dir,'Generator-R-{}'.format(version))

            with open(os.path.join(tmp_dir,'compiler_patch'), 'w') as f:
                f.write(compiler_patch)
            if subprocess.call("patch -p1 <"+os.path.join(tmp_dir,'compiler_patch'),cwd=genie_dir,shell=True):
                raise Exception('genie compiler could not be patched')
            with open(os.path.join(tmp_dir,'install_patch'), 'w') as f:
                f.write(install_patch)
            if subprocess.call("patch -p1 <"+os.path.join(tmp_dir,'install_patch'),cwd=genie_dir,shell=True):
                raise Exception('genie install could not be patched')
            
            options = [
                '--with-pythia6-lib={}'.format(os.path.join(dir_name,'lib')),
                #'--with-libxml2-inc={}'.format(os.path.join(dir_name,'include')),
                #'--with-libxml2-lib={}'.format(os.path.join(dir_name,'lib')),
                '--with-log4cpp-inc={}'.format(os.path.join(dir_name,'include')),
                '--with-log4cpp-lib={}'.format(os.path.join(dir_name,'lib')),
                '--enable-lhapdf5',
                '--with-lhapdf5-inc={}'.format(os.path.join(dir_name,'include')),
                '--with-lhapdf5-lib={}'.format(os.path.join(dir_name,'lib')),
                '--disable-lhapdf6',
            ]
            env = dict(os.environ)
            env['GENIE'] = genie_dir
            if 'CC' not in env:
                 env['CC'] = 'gcc'
            if 'CXX' not in env:
                 env['CXX'] = 'g++'

            if subprocess.call(['./configure',
                                '--prefix='+dir_name,]
                                +options,cwd=genie_dir,env=env):
                raise Exception('genie failed to cmake')
            if subprocess.call(['make'],cwd=genie_dir,env=env):
                raise Exception('genie failed to make')
            if subprocess.call(['make','install'],cwd=genie_dir,env=env):
                raise Exception('genie failed to install')
        finally:
            pass#shutil.rmtree(tmp_dir)

def versions():
    return version_dict(install)
