"""PKG_CONFIG_PATH path detection"""
import os
from util import srootbase, sroot

ret = []
for subdir in ['lib/pkgconfig','lib64/pkgconfig','share/pkgconfig']:
    path = os.path.join(sroot, subdir)
    if os.path.isdir(path):
        ret.append(path)
if 'PKG_CONFIG_PATH' in os.environ:
    ret.extend(x for x in os.environ['PKG_CONFIG_PATH'].split(':') if x.strip())
if ret:
    print(':'.join(ret))