# Copyright 2013-2018 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

#
import os
import inspect
from spack import *
from spack.util import web


class PyCryptography(PythonPackage):
    """cryptography is a package which provides cryptographic recipes
       and primitives to Python developers"""

    homepage = "https://pypi.python.org/pypi/cryptography"
    url      = "https://files.pythonhosted.org/packages/a7/9f/a725c8f434d24ae656b61539b3c3d22325e8b65331c3f8f943c4cf8858d4/cryptography-36.0.1-cp36-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.whl"

    version('36.0.1', sha256='0a817b961b46894c5ca8a66b599c745b9a3d9f822725221f0e0fe49dc043a3a3', expand=False)

    # dependencies taken from https://github.com/pyca/cryptography/blob/master/setup.py
    depends_on('py-setuptools@20.5:',   type='build')
    depends_on('py-pip',                type='build')
    depends_on('py-cffi@1.4.1:',        type=('build', 'run'))
    depends_on('py-asn1crypto@0.21.0:', type=('build', 'run'))
    depends_on('py-six@1.4.1:',         type=('build', 'run'))
    depends_on('py-idna@2.1:',          type=('build', 'run'))
    depends_on('py-enum34',             type=('build', 'run'), when='^python@:3.4')
    depends_on('py-ipaddress',          type=('build', 'run'), when='^python@:3.3')
    depends_on('openssl')

    def url_for_version(self, version):
        base_url = 'https://pypi.org/simple/cryptography/'
        filename = 'cryptography-{}-cp36-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.whl'.format(version)

        response = web._urlopen(base_url)
        readme = response.read().decode('utf-8')
        name = None
        for line in readme.split('\n'):
            if filename in line:
                return line.split('=',1)[-1].split('"',2)[1].split('#')[0]
        else:
            raise Exception('cannot find version')

    phases = ['install']

    def install(self, spec, prefix):
        """Install everything from build directory."""
        python = inspect.getmodule(self).python

        with working_dir(self.build_directory):
            whl = None
            for f in os.listdir(self.build_directory):
                if f.endswith('whl'):
                    whl = f
                    break
            if not whl:
                raise Exception('cannot find wheel')
            python('-m', 'pip', 'install', '--disable-pip-version-check', '-v', '--no-deps', '--prefix={0}'.format(prefix), whl)
