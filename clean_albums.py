#! /usr/bin/env python3

import json
import progressbar
import os
import queue
import sys
from dateutil import parser


def date_filter(lst):
    for thing in lst:
        try:
            dt = parser.parse(thing)
        except (ValueError):
            yield thing


def run(root):
    bar = progressbar.ProgressBar()
    for f in bar(os.listdir(root)):
        if os.path.splitext(f)[1] == '.json':
            with open(os.path.join(root, f)) as data_file:
                data = json.load(data_file)
                data['keywords'] = list(date_filter(data['keywords']))
                data['albums'] = list(date_filter(data['albums']))
                with open(os.path.join(root, f), 'w') as output:
                    print(json.dumps(data), file=output)

if __name__ == '__main__':
    run(sys.argv[1])
