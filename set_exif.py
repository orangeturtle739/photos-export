#! /usr/bin/env python3

import exiftool
import json
import sys
import progressbar
import os

# Copies metadata from the sidecar JSON into the file EXIF
# Copies: GPS data, rating, and albums and keywords (as tags)


def run(root):
    with exiftool.ExifTool() as et:
        def gps_opts(latitude, longitude):
            lat_ref = 'N' if latitude > 0 else 'S'
            long_ref = 'E' if longitude > 0 else 'W'
            flags = [
                'GPSLatitude=%f' %
                abs(latitude),
                'GPSLatitudeRef=%s' %
                lat_ref,
                'GPSLongitude=%f' %
                abs(longitude),
                'GPSLongitudeRef=%s' %
                long_ref]
            foo = map(lambda x: ('-EXIF:%s' % x), flags)
            return list(foo)

        def tag_opts(tags):
            return list(map(lambda x: "-XMP:TagsList='%s'" % x, tags))

        def rating_opts(rating):
            rating_map = {0: 0, 1: 1, 2: 25, 3: 50, 4: 74, 5: 99}
            return [
                '-XMP:Rating=%i' %
                rating,
                '-XMP:RatingPercent=%i' %
                rating_map[rating]]

        def exec_opts(opts, img):
            try:
                et.execute_json(*(opts + [img]))
                raise RuntimeError
            except (ValueError):
                pass

        bar = progressbar.ProgressBar()
        for f in bar(os.listdir(root)):
            if os.path.splitext(f)[1] != '.json':
                json_file = os.path.join(
                    root, os.path.splitext(f)[0] + '.json')
                img_file = os.path.join(root, f)
                with open(json_file) as data_file:
                    data = json.load(data_file)
                    opts = []
                    if data['latitude'] is not None and data[
                            'longitude'] is not None:
                        opts += gps_opts(float(data['latitude']),
                                         float(data['longitude']))
                    opts += tag_opts(data['keywords'])
                    opts += tag_opts(data['albums'])
                    opts += rating_opts(int(data['rating'] or 0))
                    if len(opts) != 0:
                        exec_opts(opts +
                                  ['-overwrite_original_in_place', '-P'], img_file)


# Usage: ./set_exif.py <output_dir>
if __name__ == '__main__':
    run(sys.argv[1])
