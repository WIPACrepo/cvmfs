"""freetype build/install"""

import os
import subprocess
import tempfile
import shutil

from build_util import wget, unpack, version_dict, cpu_cores

def install(dir_name,version=None):
    if not os.path.exists(os.path.join(dir_name,'lib','freetype.so')):
        print('installing freetype version',version)
        name = 'freetype-'+str(version)+'.tar.gz'
        try:
            tmp_dir = tempfile.mkdtemp()
            path = os.path.join(tmp_dir,name)
            url = os.path.join('http://download.savannah.gnu.org/releases/freetype',name)
            wget(url,path)
            unpack(path,tmp_dir)
            freetype_dir = os.path.join(tmp_dir,'freetype-'+version)
            if subprocess.call([os.path.join(freetype_dir,'configure'),
                                '--prefix',dir_name],
                               cwd=freetype_dir):
                raise Exception('freetype failed to configure')
            if subprocess.call(['make', '-j', cpu_cores],cwd=freetype_dir):
                raise Exception('freetype failed to make')
            if subprocess.call(['make','install'],cwd=freetype_dir):
                raise Exception('freetype failed to install')
        finally:
            shutil.rmtree(tmp_dir)

def versions():
    return version_dict(install)
