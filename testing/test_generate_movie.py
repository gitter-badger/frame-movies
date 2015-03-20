import sys
import os
sys.path.insert(0, os.path.realpath('.'))
import mimetypes

from create_movie import generate_movie


def test_generate_movie(tmpdir):
    images_dir = os.path.realpath(
            os.path.join(
                os.path.dirname(__file__),
                'fixtures'))
    output_filename = tmpdir.join('out.mp4')
    generate_movie(images_dir, str(output_filename))
    assert (os.path.isfile(str(output_filename)) and
            mimetypes.guess_type(str(output_filename)) == ('video/mp4', None))
