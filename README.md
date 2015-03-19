# Frame movies

This code takes a series of FITS files on the command line and spits out a `.mp4`.

It automatically scales the images to `+=20%` around the median and plots a time series of the median values as a function of time. Above the image is the `image_id` if present.

If the images have the shape `2048x2088` then the image is assumed to be raw and the overscan strips are removed. Otherwise they are not.

## Usage

The main script is `create_movie.py` which takes each file to add on the command line as arguments, along with the output filename with the `-o/--output` flag. Full usage is shown below.

The images require the `mjd` header card to be present unless the `--no-sort` argument is supplied, then the order the files are passed to the script is used for rendering the image.

```
usage: create_movie.py [-h] [-o OUTPUT] [--no-sort] [-f FPS]
                       [--no-multiprocessing] [-d IMAGES_DIR]
                       [--no-delete-tmpdir] [--use-mencoder] [--verbose]
                       filename [filename ...]

positional arguments:
  filename

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output movie name
  --no-sort             Do not sort by mjd
  -f FPS, --fps FPS     Frames per second
  --no-multiprocessing  Run serially
  -d IMAGES_DIR, --images-dir IMAGES_DIR
                        Custom directory to put the intermediate images
  --no-delete-tmpdir    Do not delete temporary directory of pngs
  --use-mencoder        Use mencoder instead of ffmpeg
  --verbose             Verbose logging
```

## Installation

All code is written in Python. I recommend the [Anaconda python distribution](http://continuum.io/downloads) for installation. The code either requires `ffmpeg` (preferred) or `mencoder` to render movies.

### Python dependencies

* matplotlib
* astropy
* numpy
