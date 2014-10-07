#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import

import argparse
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from multiprocessing import Pool
import tempfile
from contextlib import contextmanager
from functools import partial
import fitsio
import subprocess as sp
import shutil
import numpy as np

class NullPool(object):
    def __init__(self, *args, **kwargs): pass

    def map(self, fn, args):
        return map(fn, args)

def pack_images(dirname, output_name, kind='png'):
    full_out_path = os.path.realpath(output_name)
    with change_directory(dirname):
        cmd = ['tar', 'czf', full_out_path]
        cmd.extend([fname for fname in os.listdir('.')
                    if '.png' in fname])
        str_cmd = map(str, cmd)
        print("Running command [{}]".format(' '.join(str_cmd)))
        sp.check_call(str_cmd)


def build_image((i, input_fname), outdir, frame_min=0.8, frame_max=1.2):
    output_fname = os.path.join(outdir,
                                '{:05d}_{}.png'.format(
                                    i,
                                    os.path.basename(input_fname)))

    print("Building {}".format(output_fname))
    if os.path.isfile(output_fname):
        print("Image exists, skipping")
        return

    fig, axis = plt.subplots(figsize=(8, 8))
    with fitsio.FITS(input_fname) as infile:
        image_data = infile[0].read()

    med_image = np.median(image_data)
    z1, z2 = (med_image * frame_min, med_image * frame_max)
    axis.imshow(image_data, interpolation='None', origin='lower',
                cmap=plt.cm.afmhot, vmin=z1, vmax=z2)
    fig.tight_layout()
    fig.savefig(output_fname, bbox_inches='tight')
    plt.close(fig)

def sort_images(images):
    return sorted(images, key=lambda fname: fitsio.read_header(fname)['mjd'])

def generate_movie(image_directory, output_filename, fps):
    cmd = map(str, ['mencoder', 'mf://{}/*.png'.format(image_directory),
                    '-mf', 'w=800:h=800:fps={}:type=png'.format(fps),
                    '-ovc', 'lavc',
                    '-lavcopts', 'vcodec=mpeg4:mbd=2:turbo',
                    '-o', output_filename,
                    ])
    print(' '.join(cmd))

@contextmanager
def temporary_directory(*args, **kwargs):
    dirname = tempfile.mkdtemp(*args, **kwargs)
    try:
        yield dirname
    finally:
        shutil.rmtree(dirname)

@contextmanager
def change_directory(path):
    old_cwd = os.getcwd()
    try:
        print("Changing directory to {}".format(path))
        os.chdir(path)
        yield path
    finally:
        os.chdir(old_cwd)

def main(args):
    files = args.filename
    print('Building {} files'.format(len(files)))

    with temporary_directory() as image_dir:
        print("Building into {}".format(image_dir))

        sorted_files = sort_images(files)

        pool = Pool()
        pool.map(partial(build_image, outdir=image_dir),
                 enumerate(sorted_files))

        pack_images(image_dir, 'plots.tar.gz')


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', nargs='+')
    parser.add_argument('-o', '--output', help="Output tarball name",
                        required=False, default='plots.tar.gz')
    return parser.parse_args()


if __name__ == '__main__':
    main(parse_args())
