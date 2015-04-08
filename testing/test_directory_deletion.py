import sys
import os
sys.path.insert(0, os.path.realpath('.'))
import pytest
import string
import random

import create_movie as c


@pytest.fixture
def tmp_dirname():
    return ''.join(random.choice(
        string.ascii_uppercase + string.ascii_lowercase)
        for _ in range(10))


@pytest.fixture
def dir_path(tmp_dirname, tmpdir):
    p = str(tmpdir.join(tmp_dirname))
    assert not os.path.isdir(p)
    return p


def test_directory_deletion_with_temp_dir():
    with c.temporary_directory() as tdir:
        assert os.path.isdir(tdir)

    assert not os.path.isdir(tdir)


def test_directory_not_deleted_when_requested():
    with c.temporary_directory(delete=False) as tdir:
        assert os.path.isdir(tdir)

    assert os.path.isdir(tdir)


def test_directory_created_with_name_without_deletion(dir_path):
    with c.temporary_directory(images_dir=dir_path, delete=False) as tdir:
        assert os.path.isdir(tdir) and 'test' in tdir

    assert os.path.isdir(tdir)


def test_directory_created_with_name_with_deletion(dir_path, tmp_dirname):
    with c.temporary_directory(images_dir=dir_path, delete=True) as tdir:
        assert os.path.isdir(tdir) and os.path.split(tdir)[-1] == tmp_dirname

    assert os.path.isdir(tdir)


def test_ensure_dir(dir_path):
    c.ensure_dir(dir_path)
    assert os.path.isdir(dir_path)


def test_ensure_dir_recreates_by_default(tmpdir, tmp_dirname):
    dirname = tmpdir.mkdir(tmp_dirname)
    assert os.path.isdir(str(dirname))
    tmp_fname = 'test.txt'
    fname = dirname.join(tmp_fname)
    fname.write('Hello world')
    assert os.path.isfile(str(fname))

    c.ensure_dir(str(dirname))
    assert not os.path.isfile(str(fname))


def test_ensure_dir_leaves_if_requested(tmpdir, tmp_dirname):
    dirname = tmpdir.mkdir(tmp_dirname)
    assert os.path.isdir(str(dirname))
    tmp_fname = 'test.txt'
    fname = dirname.join(tmp_fname)
    fname.write('Hello world')
    assert os.path.isfile(str(fname))

    c.ensure_dir(str(dirname), clobber=False)
    assert os.path.isfile(str(fname))
