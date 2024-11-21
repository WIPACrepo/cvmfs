"""
OpenCL detection

Returns two ;-separated values, one for OPENCL_VENDOR_PATH, one for LD_LIBRARY_PATH
"""
import os
import tempfile
from util import srootbase, sroot, os_arch

cvmfs_ocl = os.path.join(os.path.dirname(srootbase),
                         'distrib/OpenCL_{}/etc/OpenCL/vendors'.format(os_arch))
cvmfs_lib = os.path.join(os.path.dirname(srootbase),
                         'distrib/OpenCL_{}/lib/{}'.format(os_arch, os_arch))

ocl_path = ''
if ('OPENCL_VENDOR_PATH' in os.environ and
    os.path.exists(os.environ['OPENCL_VENDOR_PATH'])):
    ocl_path = os.environ['OPENCL_VENDOR_PATH']
elif os.path.exists('/etc/OpenCL/vendors'):
    ocl_path = '/etc/OpenCL/vendors'

ld_path = ''
for path in ('/usr/lib', '/usr/lib64', '/lib', '/lib64',
             '/usr/lib/x86_64-linux-gnu', '/usr/lib/nvidia',
             '/usr/lib64/nvidia', '/usr/local/cuda/lib',
             '/usr/local/cuda/lib64', '/host-libs',
             '/opt/rocm/opencl/lib'):
    for libname in ('libOpenCL.so', 'libOpenCL.so.1', 'libOpenCL.so.1.0'):
        p = os.path.join(path, libname)
        if os.path.exists(p):
            ld_path = path
            break
    if ld_path:
        break

if os.path.isdir(ocl_path):
    # need to blend with cvmfs_ocl
    tmp_path = tempfile.mkdtemp()
    
    os.makedirs(os.path.join(tmp_path, 'etc/OpenCL/vendors'))
    for name in devices:
        path = os.path.join(tmp_path, 'etc/OpenCL/vendors', name)
        os.symlink(os.path.join(ocl_path, name), path)
    for name in os.listdir(cvmfs_ocl):
        path = os.path.join(tmp_path, 'etc/OpenCL/vendors', name)
        if not os.path.exists(path):
            os.symlink(os.path.join(cvmfs_ocl, name), path)
    ocl_path = os.path.join(tmp_path, 'etc/OpenCL/vendors')
    
    os.makedirs(os.path.join(tmp_path, 'lib'))
    for name in os.listdir(cvmfs_lib):
        if name.startswith('libOpenCL.so'):
            path = os.path.join(tmp_path, 'lib', name)
            os.symlink(os.path.join(cvmfs_lib, name), path)
    if ld_path:
        for name in os.listdir(ld_path):
            if name.startswith('libOpenCL.so'):
                path = os.path.join(tmp_path, 'lib', name)
                if not os.path.exists(path):
                    os.symlink(os.path.join(ld_path, name), path)
    ld_path = os.path.join(tmp_path, 'lib')
else:
    ocl_path = cvmfs_ocl

ld_path_list = [ld_path] if ld_path else []

# force-enable nvidia in LD_LIBRARY_PATH
for path in ('/usr/lib/nvidia', '/usr/lib64/nvidia',
             '/usr/local/cuda/lib', '/usr/local/cuda/lib64',
             '/host-libs'):
    if os.path.isdir(path):
        ld_path_list.append(path)

# force-enable AMD rocm in LD_LIBRARY_PATH
for path in ('/opt/rocm/opencl/lib',):
    if os.path.isdir(path):
        ld_path_list.append(path)

ld_path = ':'.join(ld_path_list)

print(ocl_path+';'+ld_path)
