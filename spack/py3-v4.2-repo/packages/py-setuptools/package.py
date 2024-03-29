# Copyright 2013-2018 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *


class PySetuptools(PythonPackage):
    """A Python utility that aids in the process of downloading, building,
       upgrading, installing, and uninstalling Python packages."""

    homepage = "https://github.com/pypa/setuptools"
    url      = "https://pypi.io/packages/source/s/setuptools/setuptools-40.2.0.zip"

    import_modules = [
        'setuptools', 'pkg_resources', 'setuptools._vendor',
        'setuptools.command', 'setuptools.extern',
        'setuptools._vendor.packaging', 'pkg_resources._vendor',
        'pkg_resources.extern', 'pkg_resources._vendor.packaging',
        'easy_install'
    ]

    version('40.4.3', sha256='acbc5740dd63f243f46c2b4b8e2c7fd92259c2ddb55a4115b16418a2ed371b15')
    version('40.2.0', '592efabea3a65d8e97a025ed52f69b12')
    version('39.2.0', 'dd4e3fa83a21bf7bf9c51026dc8a4e59')
    version('39.0.1', '75310b72ca0ab4e673bf7679f69d7a62')
    version('35.0.2', 'c368b4970d3ad3eab5afe4ef4dbe2437')
    version('34.4.1', '5f9b07aeaafd29eac2548fc0b89a4934')
    version('34.2.0', '41b630da4ea6cfa5894d9eb3142922be')
    version('25.2.0', 'a0dbb65889c46214c691f6c516cf959c')
    version('20.7.0', '5d12b39bf3e75e80fdce54e44b255615')
    version('20.6.7', '45d6110f3ec14924e44c33411db64fe6')
    version('20.5',   'fadc1e1123ddbe31006e5e43e927362b')
    version('19.2',   '78353b1f80375ca5e088f4b4627ffe03')
    version('18.1',   'f72e87f34fbf07f299f6cb46256a0b06')
    version('16.0',   '0ace0b96233516fc5f7c857d086aa3ad')
    version('11.3.1', '01f69212e019a2420c1693fb43593930')

    depends_on('python@2.7:2.8,3.4:', type=('build', 'run'))

    # Previously, setuptools vendored all of its dependencies to allow
    # easy bootstrapping. As of version 34.0.0, this is no longer done
    # and the dependencies need to be installed externally. As of version
    # 36.0.0, setuptools now vendors its dependencies again. See
    # https://github.com/pypa/setuptools/issues/980 for the reason they
    # reverted back to vendoring again.
    depends_on('py-packaging@16.8:', when='@34:35', type=('build', 'run'))
    depends_on('py-six@1.6.0:',      when='@34:35', type=('build', 'run'))
    depends_on('py-appdirs@1.4.0:',  when='@34:35', type=('build', 'run'))

    def url_for_version(self, version):
        url = 'https://pypi.io/packages/source/s/setuptools/setuptools-{0}'
        url = url.format(version)

        url += '.tar.gz'

        return url

    def test(self):
        # Unit tests require pytest, creating a circular dependency
        pass
