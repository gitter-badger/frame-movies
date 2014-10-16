from fabric.api import *

env.use_ssh_config = True
env.hosts = ['norwood.astro']

def pack(dirname, fname):
    local('./submit.sh {dirname} {fname}'.format(
        dirname=dirname, fname=fname))

def copy_file(fname):
    put(fname, '/tmp/plots.tar.gz')

def unpack():
    with cd('/tmp'):
        run('rm -r plots', quiet=True)
        run('mkdir plots')
        run('tar xf plots.tar.gz -C plots')

def encode():
    with cd('/tmp/plots'):
        run('~/.bin/make-movie.sh')
    print('Movie complete at /tmp/plots/output.mp4')

def make_movie(dirname, fname):
    pack(dirname, fname)
    copy_file(fname)
    unpack()
    encode()

