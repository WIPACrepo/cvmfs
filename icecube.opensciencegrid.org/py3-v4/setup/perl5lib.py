"""PERL5LIB path detection"""
import os
from util import srootbase, sroot

ret = []
for subdir in ['perl','perl5','perl5/site_perl']:
    path = os.path.join(sroot, 'lib', subdir)
    if os.path.isdir(path):
        ret.append(path)
if 'PERL5LIB' in os.environ:
    ret.extend(x for x in os.environ['PERL5LIB'].split(':') if x.strip())
if ret:
    print(':'.join(ret))