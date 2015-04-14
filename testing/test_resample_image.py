import numpy as np
import pytest
import sys
sys.path.insert(0, '.')
from create_movie import rebin


@pytest.fixture
def image():
    return np.ones(16 * 16).reshape((16, -1))


def test_rebin(image):
    assert rebin(image, (4, 4)).shape == (4, 4)


def test_rebin_values(image):
    rebinned = rebin(image, (4, 4))
    assert rebinned[0][0] == 16


def test_values_do_not_crash(image):
    rebin(image, (8, 8))
    rebin(image, (4, 4))
    rebin(image, (2, 2))
