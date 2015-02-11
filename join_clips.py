#!/usr/bin/env python
# -*- coding: utf-8 -*-

from moviepy.editor import VideoFileClip, clips_array
import argparse

def main(args):
    print(args)
    clips = map(VideoFileClip, args.file)
    final_clip = clips_array([clips])
    final_clip.write_videofile(args.output, fps=15)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', required=True)
    parser.add_argument('file', nargs='+')
    main(parser.parse_args())
