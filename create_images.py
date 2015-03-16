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


def extract_image_data(input_fname):
    with fitsio.FITS(input_fname) as infile:
        image_data = infile[0].read()
        header = infile[0].read_header()

    if image_data.shape == (2048, 2088):
        overscan = image_data[4:, -15:].mean()
        logger.warning('Image is raw, subtracting overscan {}'.format(
            overscan)
        )
        image_data = image_data[:, 20:-20] - overscan

    return header, image_data


def build_image((i, input_fname), outdir, median_behaviour,
                frame_min=0.8, frame_max=1.2):
    output_fname = os.path.join(outdir,
                                '{:05d}_{}.png'.format(
                                    i,
                                    os.path.basename(input_fname)))
    logger.debug('Building image {} => {}'.format(input_fname,
                                                  output_fname))

    if os.path.isfile(output_fname):
        logger.debug("Image {} exists, skipping".format(output_fname))
        return

    fig, axes = plt.subplots(2, 1, figsize=(8, 8),
                             gridspec_kw={'height_ratios': [0.8, 0.2]})
    header, image_data = extract_image_data(input_fname)
    med_image = np.median(image_data)
    z1, z2 = (med_image * frame_min, med_image * frame_max)
    axes[0].imshow(image_data, interpolation='None', origin='lower',
                   cmap=plt.cm.afmhot, vmin=z1, vmax=z2)
    for dimension in ['xaxis', 'yaxis']:
        getattr(axes[0], dimension).set_visible(False)
    axes[0].set_title(header.get('image_id', None))
    median_behaviour.plot(axes[1])
    median_behaviour.add_vline(axes[1], i)

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
               'crf=18:nofast_pskip:nodct_decimate:nocabac:global_header:threads={}'.format(
                   n_cpu),
               '-of', 'lavf', '-lavfopts', 'format=mp4',
               '-o', output_filename]
        sp.check_call(cmd)


@contextmanager
def temporary_directory(delete=False, *args, **kwargs):
    dirname = tempfile.mkdtemp(*args, **kwargs)
    try:
        yield dirname
    finally:
        if delete:
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


class TimeSeries(object):

    def __init__(self, x, y):
        self.x, self.y = x, y
        self.mjd0 = int(self.x.min())
        self.x -= self.mjd0

    @classmethod
    def extract_from(cls, files):
        x = np.zeros(len(files))
        y = np.zeros(len(files))

        for i, fname in enumerate(files):
            header, image_data = extract_image_data(fname)
            med_image = np.median(image_data)
            x[i] = header['mjd']
            y[i] = med_image

        return cls(x, y)

    @property
    def ylims(self):
        '''
        Return the quartiles
        '''
        return np.percentile(self.y, [2.5, 97.5])

    def plot(self, axis):
        axis.plot(self.x, self.y, '.')
        axis.set_ylim(*self.ylims)
        axis.set_xlabel('MJD - {}'.format(self.mjd0))
        axis.set_ylabel(r'Image median / ADU')

    def add_vline(self, axis, index):
        axis.axvline(self.x[index], color='k', ls='--')


def main(args):
    files = args.filename
    logger.info('Building {} files'.format(len(files)))
    if args.output is None:
        logger.warning('Not creating movie')

    with temporary_directory() as image_dir:
        logger.info("Building into {}".format(image_dir))

        sorted_files = files if args.no_sort else sort_images(files)
        logger.info('Extracting time series from data')
        median_behaviour = TimeSeries.extract_from(sorted_files)

        logger.info('Building movie images')
        pool = mp.Pool() if not args.no_multiprocessing else NullPool()
        pool.map(partial(build_image, outdir=image_dir,
                         median_behaviour=median_behaviour),
                 enumerate(sorted_files))

        if args.output is not None:
            output_filename = os.path.realpath(args.output)
            generate_movie(image_dir, output_filename, fps=args.fps)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', nargs='+')
    parser.add_argument('-o', '--output', help="Output movie name",
                        required=False)
    parser.add_argument('--no-sort', action='store_true', default=False,
                        help='Do not sort by mjd')
    parser.add_argument('-f', '--fps', help='Frames per second',
                        required=False, default=15, type=int)
    parser.add_argument('--no-multiprocessing', help='Run serially',
            action='store_true', default=False)
    parser.add_argument('-d', '--images-dir', required=False,
            help='Custom directory to put the intermediate images')
    return parser.parse_args()


if __name__ == '__main__':
    main(parse_args())
