import sys
import os
sys.path.insert(0, os.path.realpath('.'))
import pytest

from create_movie import change_directory


def test_change_directory_existing_directory(tmpdir):
    newdir = tmpdir.mkdir('subdir')
    with change_directory(str(newdir)):
        assert os.getcwd() == os.path.realpath(str(newdir))
    assert os.getcwd() != os.path.realpath(str(newdir))


def test_change_directory_non_existing_directory(tmpdir):
    pathname = tmpdir.join('subdir')
    assert not os.path.exists(str(pathname))
    with pytest.raises(OSError) as err:
        with change_directory(str(pathname)):
            pass
    assert str(pathname) in str(err)
