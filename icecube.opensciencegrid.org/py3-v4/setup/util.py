import os
import subprocess

# detect SROOTBASE and SROOT
srootbase = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os_arch = subprocess.run([os.path.join(srootbase,'os_arch.sh')], check=True,
                       encoding='utf8', stdout=subprocess.PIPE).stdout.strip()
if not os_arch:
    raise Exception('OS_ARCH not found')
sroot = os.path.join(srootbase, os_arch)