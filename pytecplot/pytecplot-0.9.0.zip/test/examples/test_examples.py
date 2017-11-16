from __future__ import unicode_literals

import platform
import shutil
import unittest

from os import path
from subprocess import Popen, PIPE

from . import run_example, outdir, masters


class TestExamples(unittest.TestCase):

    def test_00_hello_world(self):
        global outdir
        outfile = 'hello_world.png'
        out,err = run_example(self, '00_hello_world.py', [outfile])
        shutil.move(outfile, path.join(outdir,outfile))

    def test_01_load_layout_save_image(self):
        global outdir
        outfile = 'F18.jpeg'
        cmd = '01_load_layout_save_image.py'
        out,err = run_example(self, cmd, [outfile])
        self.assertRegex(out, r'INFO:tecplot.export.image:JPEG image file created: '+outfile)
        shutil.move(outfile, path.join(outdir,outfile))

    def test_02_exception_handling(self):
        global outdir
        outfile = 'spaceship.png'
        cmd = '02_exception_handling.py'
        out,err = run_example(self, cmd, [outfile])
        self.assertRegex(err, r'INFO:tecplot.export.image:PNG image file created: '+outfile)
        shutil.move(outfile, path.join(outdir,outfile))

    def test_03_slices_along_wing(self):
        global outdir
        outfiles = ['wing.png', 'wing_pressure_coefficient.png']
        cmd = '03_slices_along_wing.py'
        out,err = run_example(self, cmd, outfiles)
        for outfile in outfiles:
            self.assertRegex(out, r'INFO:tecplot.export.image:PNG image file created: '+outfile)
            shutil.move(outfile, path.join(outdir,outfile))

    def test_04_spherical_harmonic(self):
        # Skip scipy in Windows since scipy is not installable with PIP
        if platform.system() != 'Windows':
            global outdir
            outfiles = ['spherical_harmonic_4_5.lpk', 'spherical_harmonic_4_5.png']
            cmd = '04_spherical_harmonic.py'
            out,err = run_example(self, cmd, outfiles)
            self.assertRegex(err, r'INFO:tecplot.export.image:PNG image file created: '+outfiles[1])
            self.assertRegex(err, r'INFO:root:saving packaged layout file')
            for outfile in outfiles:
                shutil.move(outfile, path.join(outdir,outfile))

    def test_05_timestep_delta(self):
        global outdir
        fname = 'timestepdelta_0.000{}.png'
        outfiles = [fname.format(x) for x in ['041','082','123']]
        cmd = '05_timestep_delta.py'
        out,err = run_example(self, cmd, outfiles)
        for outfile in outfiles:
            shutil.move(outfile, path.join(outdir,outfile))

    def test_06_ndconvolution(self):
        if platform.system() != 'Windows':  # Requires scipy
            cmd = '06_ndconvolution.py'
            out,err = run_example(self, cmd, [])
            self.assertEqual(out.strip(), '[ 62688124.  73131632.  83576288. ...,  71433192.  62505044.  53579468.]', out)

    def test_07_execute_equation(self):
        global outdir
        outfiles = ['F18_orig.png', 'F18_altered.png']
        cmd = '07_execute_equation.py'
        out,err = run_example(self, cmd, outfiles)
        for outfile in outfiles:
            # self.assertRegex(out, r'INFO:tecplot.export.image:PNG image file created: '+outfile)
            shutil.move(outfile, path.join(outdir,outfile))

    def test_08_save_data(self):
        global outdir
        outfiles = ['wing.plt','wing.dat']
        cmd = '08_save_data.py'
        out,err = run_example(self, cmd, outfiles)
        for outfile in outfiles:
            shutil.move(outfile, path.join(outdir,outfile))

    def test_09_probe_at_position(self):
        cmd = '09_probe_at_position.py'
        out,err = run_example(self, cmd, [])
        self.assertEqual(out.strip(), 'C(U=0, V=0, W=10) = 1.62', out)

    def test_10_contour_filtering(self):
        global outdir
        outfile = 'contour_override.png'
        cmd = '10_contour_filtering.py'
        out,err = run_example(self, cmd, [outfile])
        shutil.move(outfile, path.join(outdir,outfile))

    def test_11_linemaps(self):
        global outdir
        outfile = 'linemap.png'
        cmd = '11_linemaps.py'
        out,err = run_example(self, cmd, [outfile])
        shutil.move(outfile, path.join(outdir,outfile))

    def test_12_slices(self):
        global outdir
        outfile = 'slice_example.png'
        cmd = '12_slices.py'
        out, err = run_example(self, cmd, [outfile])
        shutil.move(outfile, path.join(outdir, outfile))

    def test_13_wing_slices(self):
        global outdir
        outfile = 'wing_slices.png'
        cmd = '13_wing_slices.py'
        out, err = run_example(self, cmd, [outfile])
        shutil.move(outfile, path.join(outdir, outfile))

    def test_14_isosurface(self):
        global outdir
        outfile = 'isosurface_example.png'
        cmd = '14_isosurface.py'
        out, err = run_example(self, cmd, [outfile])
        shutil.move(outfile, path.join(outdir, outfile))

    def test_15_wing_mach_iso(self):
        global outdir
        outfile = 'wing_iso.png'
        cmd = '15_wing_mach_iso.py'
        out, err = run_example(self, cmd, [outfile])
        shutil.move(outfile, path.join(outdir, outfile))

    def test_16_print_zone_info(self):
        global outdir
        cmd = '16_print_zone_info.py'
        out, err = run_example(self, cmd)

    def test_17_streamtrace_line(self):
        global outdir
        outfile = 'streamtrace_line_example.png'
        cmd = '17_streamtrace_line.py'
        out, err = run_example(self, cmd, [outfile])
        shutil.move(outfile, path.join(outdir, outfile))

    def test_18_streamtrace_ribbon(self):
        global outdir
        outfile = 'streamtrace_ribbon_example.png'
        cmd = '18_streamtrace_ribbon.py'
        out, err = run_example(self, cmd, [outfile])
        shutil.move(outfile, path.join(outdir, outfile))

    def test_19_streamtrace_2D(self):
        global outdir
        outfile = 'streamtrace_2D.png'
        cmd = '19_streamtrace_2D.py'
        out, err = run_example(self, cmd, [outfile])
        shutil.move(outfile, path.join(outdir, outfile))

    def test_20_legend_line(self):
        global outdir
        outfile = 'legend_line.png'
        cmd = '20_legend_line.py'
        out, err = run_example(self, cmd, [outfile])
        shutil.move(outfile, path.join(outdir, outfile))

    def test_21_legend_contour(self):
        global outdir
        outfile = 'legend_contour.png'
        cmd = '21_legend_contour.py'
        out, err = run_example(self, cmd, [outfile])
        shutil.move(outfile, path.join(outdir, outfile))

    def test_22_view_3D(self):
        global outdir
        outfile = 'F18.jpeg'
        cmd = '22_view_3D.py'
        out, err = run_example(self, cmd, [outfile])
        shutil.move(outfile, path.join(outdir, outfile))

if __name__ == '__main__':
    from . import main
    main()
