#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import

import argparse
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import multiprocessing as mp
import tempfile
from contextlib import contextmanager
from functools import partial
import fitsio
import subprocess as sp
import shutil
import sys
import numpy as np
import logging

logger = mp.log_to_stderr()
logger.setLevel(logging.INFO)

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
        logger.debug("Running command [{}]".format(' '.join(str_cmd)))
        sp.check_call(str_cmd)


def build_image((i, input_fname), outdir, frame_min=0.8, frame_max=1.2):
    output_fname = os.path.join(outdir,
                                '{:05d}_{}.png'.format(
                                    i,
                                    os.path.basename(input_fname)))
    logger.debug('Building image {} => {}'.format(input_fname,
                                                  output_fname))

    if os.path.isfile(output_fname):
        logger.debug("Image {} exists, skipping".format(output_fname))
        return

    fig, axis = plt.subplots(figsize=(8, 8))
    with fitsio.FITS(input_fname) as infile:
        image_data = infile[0].read()
        header = infile[0].read_header()

    if image_data.shape == (2048, 2088):
        overscan = image_data[4:, -15:].mean()
        logger.warning('Image is raw, subtracting overscan {}'.format(
            overscan)
        )
        image_data = image_data[:, 20:-20] - overscan

    image_data /= header['exposure']
    med_image = np.median(image_data)
    z1, z2 = (med_image * frame_min, med_image * frame_max)
    axis.imshow(image_data, interpolation='None', origin='lower',
                cmap=plt.cm.afmhot, vmin=z1, vmax=z2)
    for dimension in ['xaxis', 'yaxis']:
        getattr(axis, dimension).set_visible(False)
    axis.set_title(header['image_id'])
    fig.tight_layout()
    fig.savefig(output_fname, bbox_inches='tight')
    plt.close(fig)

def sort_images(images):
    logger.info('Sorting images by mjd')
    return sorted(images, key=lambda fname: fitsio.read_header(fname)['mjd'])

def generate_movie(image_directory, output_filename, fps=15):
    logger.info('Building movie file {}, fps {}'.format(
        output_filename, fps)
    )
    n_cpu = mp.cpu_count()
    with change_directory(image_directory):
        cmd = ['mencoder', 'mf://*.png', '-mf',
               'w=800:h=600:fps={}:type=png'.format(fps),
                '-ovc', 'x264', '-x264encopts',
                'crf=18:nofast_pskip:nodct_decimate:nocabac:global_header:threads={}'.format(n_cpu),
                '-of', 'lavf', '-lavfopts', 'format=mp4',
                '-o', output_filename]
        sp.check_call(cmd)

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
        logger.debug("Changing directory to {}".format(path))
        os.chdir(path)
        yield path
    finally:
        os.chdir(old_cwd)

def main(args):
    files = args.filename
    output_filename = os.path.realpath(args.output)
    logger.info('Building {} files'.format(len(files)))

    with temporary_directory() as image_dir:
        logger.info("Building into {}".format(image_dir))

        sorted_files = sort_images(files)

        pool = mp.Pool()
        pool.map(partial(build_image, outdir=image_dir),
                 enumerate(sorted_files))

        generate_movie(image_dir, output_filename, fps=args.fps)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', nargs='+')
    parser.add_argument('-o', '--output', help="Output movie name",
                        required=False, default='output.mp4')
    parser.add_argument('-f', '--fps', help='Frames per second',
                        required=False, default=15, type=int)
    return parser.parse_args()


if __name__ == '__main__':
    main(parse_args())
