#! /usr/bin/env python3

import json
import progressbar
import os
import sys
from shutil import copyfile
from argparse import ArgumentParser

def run(source_dir, output_dir):
    bar = progressbar.ProgressBar()
    for f in bar(os.listdir(source_dir)):
        if os.path.splitext(f)[1] == '.json':
            with open(os.path.join(source_dir, f)) as data_file:
                data = json.load(data_file)
                for album in data['albums']:
                    album = album.replace("/", "_")
                    if not os.path.exists(os.path.join(output_dir, album)):
                        os.mkdir(os.path.join(output_dir, album))

                    imagesource = data['path']
                    imagename = data['path'].split(os.sep)[-1]
                    imagedestination = os.path.join(output_dir, album, imagename)

                    if not args.move:
                        copyfile(imagesource, imagedestination)
                    else:
                        move(imagesource, imagedestination)


# Usage: ./album_folder <source_dir> <output_dir>
# Copies all files from source_dir to a folder-based map structure in output_dir
# Useful for programs like Plex, who expect a folder-based structure for pictures
if __name__ == '__main__':

    # Options parsed from command line
    parser = ArgumentParser()
    parser.add_argument("--move", action="store_true", default=False, help='Defines if the file is to move or copy from SourceDir to DestDir')
    parser.add_argument('source_dir', help='Source from where the photos will be processed')
    parser.add_argument('output_dir', help='Destination dir of the photos')
    args = parser.parse_args()

    run(args.source_dir, args.output_dir)
