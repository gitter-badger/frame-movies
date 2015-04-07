import os
import sys
sys.path.insert(0, os.path.realpath('.'))

import create_movie as c


def test_filename_with_increment():
    outdir = 'test'
    expected = 'test/00002_test.fits.png'
    assert c.construct_output_filename(outdir, 'test.fits', 2) == expected


def test_filename_without_increment():
    outdir = 'test'
    expected = 'test/test.fits.png'
    assert c.construct_output_filename(outdir, 'test.fits', 2,
                                       include_increment=False) == expected
