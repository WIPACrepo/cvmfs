"""MANPATH path detection"""
import os
from util import srootbase, sroot

ret = []
for subdir in ['man','share/man']:
    path = os.path.join(sroot, subdir)
    if os.path.isdir(path):
        ret.append(path)
if 'MANPATH' in os.environ:
    ret.extend(x for x in os.environ['MANPATH'].split(':'))
if ret:
    if '' not in ret:
        # add default manpath config after our config
        ret.append('')
    print(':'.join(ret))