##############################################################################
# Copyright (c) 2013-2018, Lawrence Livermore National Security, LLC.
# Produced at the Lawrence Livermore National Laboratory.
#
# This file is part of Spack.
# Created by Todd Gamblin, tgamblin@llnl.gov, All rights reserved.
# LLNL-CODE-647188
#
# For details, see https://github.com/spack/spack
# Please also see the NOTICE and LICENSE files for our notice and the LGPL.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License (as
# published by the Free Software Foundation) version 2.1, February 1999.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the IMPLIED WARRANTY OF
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the terms and
# conditions of the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##############################################################################
from spack import *
from spack.util import web

import os
import glob

class Lhapdf(AutotoolsPackage):
    """LHAPDF is a general purpose C++ interpolator, used for evaluating
    PDFs from discretised data files."""

    phases = ['autoreconf', 'configure', 'build', 'install', 'download_pdfsets']

    homepage = "https://lhapdf.hepforge.org/"
    url = 'https://lhapdf.hepforge.org/downloads/?f=lhapdf-5.9.1.tar.gz'

    @when('@6:')
    def url_for_version(self, version):
        url = 'https://lhapdf.hepforge.org/downloads/?f=LHAPDF-{}.tar.gz'
        return url.format(version)

    @when('@5:')
    def url_for_version(self, version):
        url = 'https://lhapdf.hepforge.org/downloads/?f=lhapdf-{}.tar.gz'
        return url.format(version)

    version('5.9.1', sha256='86b9b046d7f25627ce2aab6847ef1c5534972f4bae18de98225080cf5086919c')

    pdfsets = ['mrst', 'mrst06', 'mrst98', 'mrstqed', 'cteq', 'grv',
               'nnpdf', 'mstw', 'gjr', 'h1', 'zeus', 'hera', 'alekhin',
               'botje', 'fermi', 'hkn', 'pions', 'photons', 'user']

    variant('shared', default=True, description='Build shared libraries')
    variant('static', default=True, description='Build static libraries')
    variant('python', default=False, description='Build python extension')
    variant('octave', default=False, description='Build octave interface')
    for pdf in pdfsets:
        variant('pdfset-'+pdf, default=True, description='Include pdf set '+pdf)
    
    variant('download-pdfsets', default=False, description='Download pdf sets')

    depends_on('wget', when='+download-pdfsets', type='build')
    depends_on('python', when='+python', type=('build','run'))
    depends_on('octave', when='+octave', type=('build','run'))

    def configure_args(self):
        spec = self.spec
        if spec.satisfies('@5:5.9.9'):
            args = ['--disable-old-ccwrap', '--disable-doxygen', '--with-pic']
        else:
            args = ['--with-pic']

        if '+shared' in spec:
            args.append('--enable-shared')
        else:
            args.append('--disable-shared')

        if '+static' in spec:
            args.append('--enable-static')
        else:
            args.append('--disable-static')

        if '+python' in spec:
            if spec.satisfies('@5:5.9.9'):
                args.append('--enable-pyext')
            else:
                args.append('--enable-python')
            self.env.set('PYTHON', selp.spec['python'].executable)
        else:
            if spec.satisfies('@5:5.9.9'):
                args.append('--disable-pyext')
            else:
                args.append('--disable-python')

        if spec.satisfies('@5:5.9.9'):
            if '+octave' in spec:
                args.append('--enable-octave')
            else:
                args.append('--disable-octave')

        if spec.satisfies('@5:5.9.9'):
            install_pdf = []
            for pdf in self.pdfsets:
                if '+pdfset-'+pdf in spec:
                    install_pdf.append(pdf)
            if install_pdf:
                args.append('--enable-pdfsets={}'.format(','.join(install_pdf)))

        return args

    def download_pdfsets(self, *args, **kwargs):
        if '+download-pdfsets' in self.spec:
            path = os.path.join(self.prefix, 'share', 'lhapdf','PDFsets')
            os.makedirs(path)

            download_url = 'https://lhapdf.hepforge.org/downloads/?f=pdfsets/{}/{}'
            wget = which('wget')

            for pdf in self.pdfset_resources:
                download_path = os.path.join(path, pdf)
                if not os.path.exists(download_path):
                    wget('--no-verbose', '-O', download_path, download_url.format(self.version, pdf))

    pdfset_resources = [
        'ABFKWPI.LHgrid',
        'ACFGPG.LHgrid',
        'ATLAS-epWZ12-EIG.LHgrid',
        'ATLAS-epWZ12-VAR.LHgrid',
        'Alekhin_100.LHpdf',
        'Alekhin_1000.LHpdf',
        'Botje_100.LHpdf',
        'Botje_1000.LHpdf',
        'CJ12max.LHgrid',
        'CJ12mid.LHgrid',
        'CJ12min.LHgrid',
        'CT09MC1.LHgrid',
        'CT09MC2.LHgrid',
        'CT09MCS.LHgrid',
        'CT10.LHgrid',
        'CT10as.LHgrid',
        'CT10f3.LHgrid',
        'CT10f4.LHgrid',
        'CT10nlo.LHgrid',
        'CT10nlo_as_0112.LHgrid',
        'CT10nlo_as_0113.LHgrid',
        'CT10nlo_as_0114.LHgrid',
        'CT10nlo_as_0115.LHgrid',
        'CT10nlo_as_0116.LHgrid',
        'CT10nlo_as_0117.LHgrid',
        'CT10nlo_as_0118.LHgrid',
        'CT10nlo_as_0119.LHgrid',
        'CT10nlo_as_0120.LHgrid',
        'CT10nlo_as_0121.LHgrid',
        'CT10nlo_as_0122.LHgrid',
        'CT10nlo_as_0123.LHgrid',
        'CT10nlo_as_0124.LHgrid',
        'CT10nlo_as_0125.LHgrid',
        'CT10nlo_as_0126.LHgrid',
        'CT10nlo_as_0127.LHgrid',
        'CT10nlo_nf3.LHgrid',
        'CT10nlo_nf4.LHgrid',
        'CT10nnlo.LHgrid',
        'CT10nnlo_as_0110.LHgrid',
        'CT10nnlo_as_0111.LHgrid',
        'CT10nnlo_as_0112.LHgrid',
        'CT10nnlo_as_0113.LHgrid',
        'CT10nnlo_as_0114.LHgrid',
        'CT10nnlo_as_0115.LHgrid',
        'CT10nnlo_as_0116.LHgrid',
        'CT10nnlo_as_0117.LHgrid',
        'CT10nnlo_as_0118.LHgrid',
        'CT10nnlo_as_0119.LHgrid',
        'CT10nnlo_as_0120.LHgrid',
        'CT10nnlo_as_0121.LHgrid',
        'CT10nnlo_as_0122.LHgrid',
        'CT10nnlo_as_0123.LHgrid',
        'CT10nnlo_as_0124.LHgrid',
        'CT10nnlo_as_0125.LHgrid',
        'CT10nnlo_as_0126.LHgrid',
        'CT10nnlo_as_0127.LHgrid',
        'CT10nnlo_as_0128.LHgrid',
        'CT10nnlo_as_0129.LHgrid',
        'CT10nnlo_as_0130.LHgrid',
        'CT10w.LHgrid',
        'CT10was.LHgrid',
        'CT10wf3.LHgrid',
        'CT10wf4.LHgrid',
        'CT10wnlo.LHgrid',
        'CT10wnlo_as_0112.LHgrid',
        'CT10wnlo_as_0113.LHgrid',
        'CT10wnlo_as_0114.LHgrid',
        'CT10wnlo_as_0115.LHgrid',
        'CT10wnlo_as_0116.LHgrid',
        'CT10wnlo_as_0117.LHgrid',
        'CT10wnlo_as_0118.LHgrid',
        'CT10wnlo_as_0119.LHgrid',
        'CT10wnlo_as_0120.LHgrid',
        'CT10wnlo_as_0121.LHgrid',
        'CT10wnlo_as_0122.LHgrid',
        'CT10wnlo_as_0123.LHgrid',
        'CT10wnlo_as_0124.LHgrid',
        'CT10wnlo_as_0125.LHgrid',
        'CT10wnlo_as_0126.LHgrid',
        'CT10wnlo_as_0127.LHgrid',
        'CT10wnlo_nf3.LHgrid',
        'CT10wnlo_nf4.LHgrid',
        'DGG.LHgrid',
        'DOG0.LHgrid',
        'DOG1.LHgrid',
        'EPS09LOR_108.LHgrid',
        'EPS09LOR_115.LHgrid',
        'EPS09LOR_117.LHgrid',
        'EPS09LOR_12.LHgrid',
        'EPS09LOR_16.LHgrid',
        'EPS09LOR_184.LHgrid',
        'EPS09LOR_195.LHgrid',
        'EPS09LOR_197.LHgrid',
        'EPS09LOR_208.LHgrid',
        'EPS09LOR_238.LHgrid',
        'EPS09LOR_27.LHgrid',
        'EPS09LOR_4.LHgrid',
        'EPS09LOR_40.LHgrid',
        'EPS09LOR_56.LHgrid',
        'EPS09LOR_6.LHgrid',
        'EPS09LOR_64.LHgrid',
        'EPS09LOR_9.LHgrid',
        'EPS09NLOR_108.LHgrid',
        'EPS09NLOR_115.LHgrid',
        'EPS09NLOR_117.LHgrid',
        'EPS09NLOR_12.LHgrid',
        'EPS09NLOR_131.LHgrid',
        'EPS09NLOR_16.LHgrid',
        'EPS09NLOR_184.LHgrid',
        'EPS09NLOR_195.LHgrid',
        'EPS09NLOR_197.LHgrid',
        'EPS09NLOR_20.LHgrid',
        'EPS09NLOR_208.LHgrid',
        'EPS09NLOR_238.LHgrid',
        'EPS09NLOR_27.LHgrid',
        'EPS09NLOR_4.LHgrid',
        'EPS09NLOR_40.LHgrid',
        'EPS09NLOR_56.LHgrid',
        'EPS09NLOR_6.LHgrid',
        'EPS09NLOR_64.LHgrid',
        'EPS09NLOR_84.LHgrid',
        'EPS09NLOR_9.LHgrid',
        'Fermi2002_100.LHpdf',
        'Fermi2002_1000.LHpdf',
        'GJR08FFdis.LHgrid',
        'GJR08FFnloE.LHgrid',
        'GJR08VFnloE.LHgrid',
        'GJR08lo.LHgrid',
        'GRV98lo.LHgrid',
        'GRV98nlo.LHgrid',
        'GRVG0.LHgrid',
        'GRVG1.LHgrid',
        'GRVPI0.LHgrid',
        'GRVPI1.LHgrid',
        'GSG0.LHgrid',
        'GSG1.LHgrid',
        'GSG960.LHgrid',
        'GSG961.LHgrid',
        'H12000dis.LHgrid',
        'H12000disE.LHgrid',
        'H12000lo.LHgrid',
        'H12000loE.LHgrid',
        'H12000ms.LHgrid',
        'H12000msE.LHgrid',
        'HERAPDF01.LHgrid',
        'HERAPDF01.LHpdf',
        'HERAPDF1.5LO_EIG.LHgrid',
        'HERAPDF10_ALPHAS.LHgrid',
        'HERAPDF10_EIG.LHgrid',
        'HERAPDF10_FF.LHgrid',
        'HERAPDF10_FFMOD.LHgrid',
        'HERAPDF10_VAR.LHgrid',
        'HERAPDF15NLO_ALPHAS.LHgrid',
        'HERAPDF15NLO_EIG.LHgrid',
        'HERAPDF15NLO_VAR.LHgrid',
        'HERAPDF15NNLO_ALPHAS.LHgrid',
        'HERAPDF15NNLO_EIG.LHgrid',
        'HERAPDF15NNLO_VAR.LHgrid',
        'HKNlo.LHgrid',
        'HKNnlo.LHgrid',
        'JR09FFnnloE.LHgrid',
        'JR09VFnnloE.LHgrid',
        'LACG.LHgrid',
        'LHECNLO_EIG.LHgrid',
        'MRST2001E.LHgrid',
        'MRST2001E.LHpdf',
        'MRST2001lo.LHgrid',
        'MRST2001nlo.LHgrid',
        'MRST2001nlo.LHpdf',
        'MRST2001nnlo.LHgrid',
        'MRST2002nlo.LHgrid',
        'MRST2002nlo.LHpdf',
        'MRST2002nnlo.LHgrid',
        'MRST2003cnlo.LHgrid',
        'MRST2003cnlo.LHpdf',
        'MRST2003cnnlo.LHgrid',
        'MRST2004FF3lo.LHgrid',
        'MRST2004FF3nlo.LHgrid',
        'MRST2004FF3nlo.LHpdf',
        'MRST2004FF4lo.LHgrid',
        'MRST2004FF4nlo.LHgrid',
        'MRST2004FF4nlo.LHpdf',
        'MRST2004nlo.LHgrid',
        'MRST2004nlo.LHpdf',
        'MRST2004nnlo.LHgrid',
        'MRST2004qed.LHgrid',
        'MRST2004qed_neutron.LHgrid',
        'MRST2004qed_proton.LHgrid',
        'MRST2006nnlo.LHgrid',
        'MRST2007lomod.LHgrid',
        'MRST98.LHpdf',
        'MRST98dis.LHgrid',
        'MRST98ht.LHgrid',
        'MRST98lo.LHgrid',
        'MRST98nlo.LHgrid',
        'MRSTMCal.LHgrid',
        'MSTW2008CPdeutnlo68cl.LHgrid',
        'MSTW2008CPdeutnnlo68cl.LHgrid',
        'MSTW2008lo68cl.LHgrid',
        'MSTW2008lo68cl_nf3.LHgrid',
        'MSTW2008lo68cl_nf4.LHgrid',
        'MSTW2008lo68cl_nf4as5.LHgrid',
        'MSTW2008lo90cl.LHgrid',
        'MSTW2008lo90cl_nf3.LHgrid',
        'MSTW2008lo90cl_nf4.LHgrid',
        'MSTW2008lo90cl_nf4as5.LHgrid',
        'MSTW2008nlo68cl.LHgrid',
        'MSTW2008nlo68cl_asmz+68cl.LHgrid',
        'MSTW2008nlo68cl_asmz+68clhalf.LHgrid',
        'MSTW2008nlo68cl_asmz-68cl.LHgrid',
        'MSTW2008nlo68cl_asmz-68clhalf.LHgrid',
        'MSTW2008nlo68cl_nf3.LHgrid',
        'MSTW2008nlo68cl_nf4.LHgrid',
        'MSTW2008nlo68cl_nf4as5.LHgrid',
        'MSTW2008nlo90cl.LHgrid',
        'MSTW2008nlo90cl_asmz+90cl.LHgrid',
        'MSTW2008nlo90cl_asmz+90clhalf.LHgrid',
        'MSTW2008nlo90cl_asmz-90cl.LHgrid',
        'MSTW2008nlo90cl_asmz-90clhalf.LHgrid',
        'MSTW2008nlo90cl_nf3.LHgrid',
        'MSTW2008nlo90cl_nf4.LHgrid',
        'MSTW2008nlo90cl_nf4as5.LHgrid',
        'MSTW2008nlo_asmzrange.LHgrid',
        'MSTW2008nlo_mbrange.LHgrid',
        'MSTW2008nlo_mbrange_nf4.LHgrid',
        'MSTW2008nlo_mcrange.LHgrid',
        'MSTW2008nlo_mcrange_fixasmz.LHgrid',
        'MSTW2008nlo_mcrange_fixasmz_nf3.LHgrid',
        'MSTW2008nlo_mcrange_nf3.LHgrid',
        'MSTW2008nnlo68cl.LHgrid',
        'MSTW2008nnlo68cl_asmz+68cl.LHgrid',
        'MSTW2008nnlo68cl_asmz+68clhalf.LHgrid',
        'MSTW2008nnlo68cl_asmz-68cl.LHgrid',
        'MSTW2008nnlo68cl_asmz-68clhalf.LHgrid',
        'MSTW2008nnlo68cl_nf3.LHgrid',
        'MSTW2008nnlo68cl_nf4.LHgrid',
        'MSTW2008nnlo68cl_nf4as5.LHgrid',
        'MSTW2008nnlo90cl.LHgrid',
        'MSTW2008nnlo90cl_asmz+90cl.LHgrid',
        'MSTW2008nnlo90cl_asmz+90clhalf.LHgrid',
        'MSTW2008nnlo90cl_asmz-90cl.LHgrid',
        'MSTW2008nnlo90cl_asmz-90clhalf.LHgrid',
        'MSTW2008nnlo90cl_nf3.LHgrid',
        'MSTW2008nnlo90cl_nf4.LHgrid',
        'MSTW2008nnlo90cl_nf4as5.LHgrid',
        'MSTW2008nnlo_asmzrange.LHgrid',
        'MSTW2008nnlo_mbrange.LHgrid',
        'MSTW2008nnlo_mbrange_nf4.LHgrid',
        'MSTW2008nnlo_mcrange.LHgrid',
        'MSTW2008nnlo_mcrange_fixasmz.LHgrid',
        'MSTW2008nnlo_mcrange_fixasmz_nf3.LHgrid',
        'MSTW2008nnlo_mcrange_nf3.LHgrid',
        'NNPDF10_100.LHgrid',
        'NNPDF10_100.LHpdf',
        'NNPDF10_1000.LHgrid',
        'NNPDF10_1000.LHpdf',
        'NNPDF11_100.LHgrid',
        'NNPDF12_100.LHgrid',
        'NNPDF12_1000.LHgrid',
        'NNPDF20_100.LHgrid',
        'NNPDF20_1000.LHgrid',
        'NNPDF20_as_0114_100.LHgrid',
        'NNPDF20_as_0115_100.LHgrid',
        'NNPDF20_as_0116_100.LHgrid',
        'NNPDF20_as_0117_100.LHgrid',
        'NNPDF20_as_0118_100.LHgrid',
        'NNPDF20_as_0120_100.LHgrid',
        'NNPDF20_as_0121_100.LHgrid',
        'NNPDF20_as_0122_100.LHgrid',
        'NNPDF20_as_0123_100.LHgrid',
        'NNPDF20_as_0124_100.LHgrid',
        'NNPDF20_dis+dy_100.LHgrid',
        'NNPDF20_dis+jet_100.LHgrid',
        'NNPDF20_dis_100.LHgrid',
        'NNPDF20_heraold_100.LHgrid',
        'NNPDF21_100.LHgrid',
        'NNPDF21_1000.LHgrid',
        'NNPDF21_FFN_NF3_100.LHgrid',
        'NNPDF21_FFN_NF4_100.LHgrid',
        'NNPDF21_FFN_NF5_100.LHgrid',
        'NNPDF21_as_0114_100.LHgrid',
        'NNPDF21_as_0115_100.LHgrid',
        'NNPDF21_as_0116_100.LHgrid',
        'NNPDF21_as_0117_100.LHgrid',
        'NNPDF21_as_0118_100.LHgrid',
        'NNPDF21_as_0120_100.LHgrid',
        'NNPDF21_as_0121_100.LHgrid',
        'NNPDF21_as_0122_100.LHgrid',
        'NNPDF21_as_0123_100.LHgrid',
        'NNPDF21_as_0124_100.LHgrid',
        'NNPDF21_dis+dy_100.LHgrid',
        'NNPDF21_dis+jet_100.LHgrid',
        'NNPDF21_dis_100.LHgrid',
        'NNPDF21_dis_1000.LHgrid',
        'NNPDF21_lo_as_0119_100.LHgrid',
        'NNPDF21_lo_as_0130_100.LHgrid',
        'NNPDF21_lostar_as_0119_100.LHgrid',
        'NNPDF21_lostar_as_0130_100.LHgrid',
        'NNPDF21_mb_425_100.LHgrid',
        'NNPDF21_mb_45_100.LHgrid',
        'NNPDF21_mb_50_100.LHgrid',
        'NNPDF21_mb_525_100.LHgrid',
        'NNPDF21_mc_15_100.LHgrid',
        'NNPDF21_mc_16_100.LHgrid',
        'NNPDF21_mc_17_100.LHgrid',
        'NNPDF21_nnlo_100.LHgrid',
        'NNPDF21_nnlo_1000.LHgrid',
        'NNPDF21_nnlo_as_0114_100.LHgrid',
        'NNPDF21_nnlo_as_0115_100.LHgrid',
        'NNPDF21_nnlo_as_0116_100.LHgrid',
        'NNPDF21_nnlo_as_0117_100.LHgrid',
        'NNPDF21_nnlo_as_0118_100.LHgrid',
        'NNPDF21_nnlo_as_0120_100.LHgrid',
        'NNPDF21_nnlo_as_0121_100.LHgrid',
        'NNPDF21_nnlo_as_0122_100.LHgrid',
        'NNPDF21_nnlo_as_0123_100.LHgrid',
        'NNPDF21_nnlo_as_0124_100.LHgrid',
        'NNPDF21_nnlo_collider_100.LHgrid',
        'NNPDF21_nnlo_dis+dy_100.LHgrid',
        'NNPDF21_nnlo_dis_100.LHgrid',
        'NNPDF21_nnlo_heraonly_100.LHgrid',
        'NNPDF21_nnlo_mb_425_100.LHgrid',
        'NNPDF21_nnlo_mb_45_100.LHgrid',
        'NNPDF21_nnlo_mb_50_100.LHgrid',
        'NNPDF21_nnlo_mb_525_100.LHgrid',
        'NNPDF21_nnlo_mc_15_100.LHgrid',
        'NNPDF21_nnlo_mc_16_100.LHgrid',
        'NNPDF21_nnlo_mc_17_100.LHgrid',
        'NNPDF21_nnlo_nf5_100.LHgrid',
        'NNPDF22_nlo_100.LHgrid',
        'NNPDF23_nlo_FFN_NF4_as_0116.LHgrid',
        'NNPDF23_nlo_FFN_NF4_as_0116_mc.LHgrid',
        'NNPDF23_nlo_FFN_NF4_as_0117.LHgrid',
        'NNPDF23_nlo_FFN_NF4_as_0117_mc.LHgrid',
        'NNPDF23_nlo_FFN_NF4_as_0118.LHgrid',
        'NNPDF23_nlo_FFN_NF4_as_0118_mc.LHgrid',
        'NNPDF23_nlo_FFN_NF4_as_0119.LHgrid',
        'NNPDF23_nlo_FFN_NF4_as_0119_mc.LHgrid',
        'NNPDF23_nlo_FFN_NF4_as_0120.LHgrid',
        'NNPDF23_nlo_FFN_NF4_as_0120_mc.LHgrid',
        'NNPDF23_nlo_FFN_NF5_as_0116.LHgrid',
        'NNPDF23_nlo_FFN_NF5_as_0116_mc.LHgrid',
        'NNPDF23_nlo_FFN_NF5_as_0117.LHgrid',
        'NNPDF23_nlo_FFN_NF5_as_0117_mc.LHgrid',
        'NNPDF23_nlo_FFN_NF5_as_0118.LHgrid',
        'NNPDF23_nlo_FFN_NF5_as_0118_mc.LHgrid',
        'NNPDF23_nlo_FFN_NF5_as_0119.LHgrid',
        'NNPDF23_nlo_FFN_NF5_as_0119_mc.LHgrid',
        'NNPDF23_nlo_FFN_NF5_as_0120.LHgrid',
        'NNPDF23_nlo_FFN_NF5_as_0120_mc.LHgrid',
        'NNPDF23_nlo_as_0114.LHgrid',
        'NNPDF23_nlo_as_0115.LHgrid',
        'NNPDF23_nlo_as_0116.LHgrid',
        'NNPDF23_nlo_as_0116_mc.LHgrid',
        'NNPDF23_nlo_as_0117.LHgrid',
        'NNPDF23_nlo_as_0117_mc.LHgrid',
        'NNPDF23_nlo_as_0117_qed.LHgrid',
        'NNPDF23_nlo_as_0117_qed_neutron.LHgrid',
        'NNPDF23_nlo_as_0118.LHgrid',
        'NNPDF23_nlo_as_0118_mc.LHgrid',
        'NNPDF23_nlo_as_0118_qed.LHgrid',
        'NNPDF23_nlo_as_0118_qed_neutron.LHgrid',
        'NNPDF23_nlo_as_0119.LHgrid',
        'NNPDF23_nlo_as_0119_mc.LHgrid',
        'NNPDF23_nlo_as_0119_qed.LHgrid',
        'NNPDF23_nlo_as_0119_qed_neutron.LHgrid',
        'NNPDF23_nlo_as_0120.LHgrid',
        'NNPDF23_nlo_as_0120_mc.LHgrid',
        'NNPDF23_nlo_as_0121.LHgrid',
        'NNPDF23_nlo_as_0122.LHgrid',
        'NNPDF23_nlo_as_0123.LHgrid',
        'NNPDF23_nlo_as_0124.LHgrid',
        'NNPDF23_nlo_collider_as_0116.LHgrid',
        'NNPDF23_nlo_collider_as_0117.LHgrid',
        'NNPDF23_nlo_collider_as_0118.LHgrid',
        'NNPDF23_nlo_collider_as_0119.LHgrid',
        'NNPDF23_nlo_collider_as_0120.LHgrid',
        'NNPDF23_nlo_noLHC_as_0116.LHgrid',
        'NNPDF23_nlo_noLHC_as_0117.LHgrid',
        'NNPDF23_nlo_noLHC_as_0118.LHgrid',
        'NNPDF23_nlo_noLHC_as_0119.LHgrid',
        'NNPDF23_nlo_noLHC_as_0120.LHgrid',
        'NNPDF23_nnlo_FFN_NF4_as_0116.LHgrid',
        'NNPDF23_nnlo_FFN_NF4_as_0117.LHgrid',
        'NNPDF23_nnlo_FFN_NF4_as_0118.LHgrid',
        'NNPDF23_nnlo_FFN_NF4_as_0119.LHgrid',
        'NNPDF23_nnlo_FFN_NF4_as_0120.LHgrid',
        'NNPDF23_nnlo_FFN_NF5_as_0116.LHgrid',
        'NNPDF23_nnlo_FFN_NF5_as_0117.LHgrid',
        'NNPDF23_nnlo_FFN_NF5_as_0118.LHgrid',
        'NNPDF23_nnlo_FFN_NF5_as_0119.LHgrid',
        'NNPDF23_nnlo_FFN_NF5_as_0120.LHgrid',
        'NNPDF23_nnlo_as_0114.LHgrid',
        'NNPDF23_nnlo_as_0115.LHgrid',
        'NNPDF23_nnlo_as_0116.LHgrid',
        'NNPDF23_nnlo_as_0117.LHgrid',
        'NNPDF23_nnlo_as_0117_qed.LHgrid',
        'NNPDF23_nnlo_as_0117_qed_neutron.LHgrid',
        'NNPDF23_nnlo_as_0118.LHgrid',
        'NNPDF23_nnlo_as_0118_qed.LHgrid',
        'NNPDF23_nnlo_as_0118_qed_neutron.LHgrid',
        'NNPDF23_nnlo_as_0119.LHgrid',
        'NNPDF23_nnlo_as_0119_qed.LHgrid',
        'NNPDF23_nnlo_as_0119_qed_neutron.LHgrid',
        'NNPDF23_nnlo_as_0120.LHgrid',
        'NNPDF23_nnlo_as_0121.LHgrid',
        'NNPDF23_nnlo_as_0122.LHgrid',
        'NNPDF23_nnlo_as_0123.LHgrid',
        'NNPDF23_nnlo_as_0124.LHgrid',
        'NNPDF23_nnlo_collider_as_0116.LHgrid',
        'NNPDF23_nnlo_collider_as_0117.LHgrid',
        'NNPDF23_nnlo_collider_as_0118.LHgrid',
        'NNPDF23_nnlo_collider_as_0119.LHgrid',
        'NNPDF23_nnlo_collider_as_0120.LHgrid',
        'NNPDF23_nnlo_noLHC_as_0116.LHgrid',
        'NNPDF23_nnlo_noLHC_as_0117.LHgrid',
        'NNPDF23_nnlo_noLHC_as_0118.LHgrid',
        'NNPDF23_nnlo_noLHC_as_0119.LHgrid',
        'NNPDF23_nnlo_noLHC_as_0120.LHgrid',
        'NNPDFpol10_100.LHgrid',
        'OWPI.LHgrid',
        'SASG.LHgrid',
        'SMRSPI.LHgrid',
        'USERGRIDQ2.LHgrid',
        'USERGRIDQ3.LHgrid',
        'USERGRIDQ4.LHgrid',
        'WHITG.LHgrid',
        'ZEUS2002_FF.LHpdf',
        'ZEUS2002_TR.LHpdf',
        'ZEUS2002_ZM.LHpdf',
        'ZEUS2005_ZJ.LHpdf',
        'a02m_lo.LHgrid',
        'a02m_nlo.LHgrid',
        'a02m_nnlo.LHgrid',
        'abkm09_3_nlo.LHgrid',
        'abkm09_3_nnlo.LHgrid',
        'abkm09_4_nlo.LHgrid',
        'abkm09_4_nnlo.LHgrid',
        'abkm09_5_nlo.LHgrid',
        'abkm09_5_nnlo.LHgrid',
        'abm11_3n_nlo.LHgrid',
        'abm11_3n_nnlo.LHgrid',
        'abm11_4n_nlo.LHgrid',
        'abm11_4n_nnlo.LHgrid',
        'abm11_5n_as_nlo.LHgrid',
        'abm11_5n_as_nnlo.LHgrid',
        'abm11_5n_nlo.LHgrid',
        'abm11_5n_nnlo.LHgrid',
        'abm12lhc_3_nnlo.LHgrid',
        'abm12lhc_4_nnlo.LHgrid',
        'abm12lhc_5_nnlo.LHgrid',
        'cteq4d.LHgrid',
        'cteq4l.LHgrid',
        'cteq4m.LHgrid',
        'cteq5d.LHgrid',
        'cteq5f3.LHgrid',
        'cteq5f4.LHgrid',
        'cteq5l.LHgrid',
        'cteq5m.LHgrid',
        'cteq5m1.LHgrid',
        'cteq6.LHpdf',
        'cteq61.LHgrid',
        'cteq61.LHpdf',
        'cteq65.LHgrid',
        'cteq65c.LHgrid',
        'cteq65s.LHgrid',
        'cteq66.LHgrid',
        'cteq66a0.LHgrid',
        'cteq66a1.LHgrid',
        'cteq66a2.LHgrid',
        'cteq66a3.LHgrid',
        'cteq66alphas.LHgrid',
        'cteq66c.LHgrid',
        'cteq6AB.LHgrid',
        'cteq6l.LHpdf',
        'cteq6lg.LHgrid',
        'cteq6ll.LHpdf',
        'cteq6m.LHpdf',
        'cteq6mE.LHgrid',
        'eps08dta.LHgrid',
    ]
