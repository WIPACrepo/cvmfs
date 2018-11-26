"""lhapdf5 build/install"""

import os
import subprocess
import tempfile
import shutil

from build_util import wget, unpack, version_dict, cpu_cores

def install(dir_name,version=None):
    if not os.path.exists(os.path.join(dir_name,'bin','lhapdf-config')):
        print('installing lhapdf5 version',version)
        name = 'lhapdf-'+str(version)+'.tar.gz'
        try:
            tmp_dir = tempfile.mkdtemp()
            path = os.path.join(tmp_dir,name)
            url = os.path.join('https://lhapdf.hepforge.org/downloads/?f='+name)
            wget(url,path)
            unpack(path,tmp_dir)
            lhapdf5_dir = os.path.join(tmp_dir,'lhapdf-'+version)

            pdfsets = ['mrst', 'mrst06', 'mrst98', 'mrstqed', 'cteq', 'grv',
                       'nnpdf', 'mstw', 'gjr', 'h1', 'zeus', 'hera', 'alekhin',
                       'botje', 'fermi', 'hkn', 'pions', 'photons', 'user']
            options = [
                '--disable-old-ccwrap',
                '--disable-doxygen',
                '--with-pic',
                '--enable-shared',
                '--enable-static',
                '--disable-pyext',
                '--disable-octave',
                '--enable-pdfsets={}'.format(','.join(pdfsets)),
            ]
            if subprocess.call([os.path.join(lhapdf5_dir,'configure'),
                                '--prefix',dir_name]+options,
                               cwd=lhapdf5_dir):
                raise Exception('lhapdf5 failed to configure')
            if subprocess.call(['make', '-j', cpu_cores],cwd=lhapdf5_dir):
                raise Exception('lhapdf5 failed to make')
            if subprocess.call(['make','install'],cwd=lhapdf5_dir):
                raise Exception('lhapdf5 failed to install')
        finally:
            shutil.rmtree(tmp_dir)

def versions():
    return version_dict(install)
