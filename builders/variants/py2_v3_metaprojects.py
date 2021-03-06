# build the /py2-v1 directory, for this OS

import sys
import os
import subprocess
import tempfile
import shutil

from build_util import *

tools = get_tools()

def build(src,dest,svn_up=None,svn_only=None,nightly=False,**build_kwargs):
    """The main builder"""
    # first, make sure the base dir is there
    dir_name = os.path.join(dest,'py2-v3')
    if not os.path.isdir(dir_name):
        raise Exception('base does not exist')

    # now, do the OS-specific stuff
    load_env(dir_name)
    if 'SROOT' not in os.environ:
        raise Exception('$SROOT not defined')
    dir_name = os.environ['SROOT']

    kwargs = {}
    if svn_up is not None:
        kwargs['svn_up'] = svn_up
    if svn_only is not None:
        kwargs['svn_only'] = svn_only

    # releases
    tools['i3_metaproject']['simulation']['V05-02-00'](dir_name,**kwargs)
    tools['i3_metaproject']['simulation']['V06-00-00'](dir_name,**kwargs)
    tools['i3_metaproject']['simulation']['V06-00-01'](dir_name,**kwargs)
    #tools['i3_metaproject']['simulation']['V06-00-02-RC1'](dir_name,**kwargs)
    #tools['i3_metaproject']['simulation']['V06-00-02-RC2'](dir_name,**kwargs)

    tools['i3_metaproject']['icerec']['V05-02-00'](dir_name,**kwargs)

#    if nightly:
        # trunks
#        tools['i3_metaproject']['combo']['stable'](dir_name,**kwargs)

