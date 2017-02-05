#! /usr/bin/env python3

import json
import progressbar
import os
import queue
import sys
import sqlite3
import glob
from dateutil import parser

# Digikam format
# edited_id original_id 2

# Determine the ID of an image in the Digikam database


def image_id(db, name):
    c = db.cursor()
    c.execute('SELECT * FROM Images WHERE name=?', [os.path.basename(name)])
    rows = c.fetchall()
    if len(rows) != 1:
        raise RuntimeError('Too many matches for "%s": %i' % (name, len(rows)))
    return rows[0]['id']

# Run on the output folder (should be the root digikam folder)


def run(root):
    db_path = os.path.join(root, 'digikam4.db')
    db = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row

    bar = progressbar.ProgressBar()
    for f in bar(os.listdir(root)):
        found_ext = os.path.splitext(f)[1]
        if found_ext != '.json' and found_ext != '.db':
            json_file = os.path.join(
                root, os.path.splitext(f)[0] + '.json')
            img_file = os.path.join(root, f)
            with open(json_file) as data_file:
                data = json.load(data_file)
                derived_from = data['derived_from']
                if derived_from is not None:
                    edited_id = image_id(db, img_file)
                    possible_originals = glob.glob(
                        os.path.join(root, derived_from) + '.*')
                    possible_originals = [
                        item for item in possible_originals if os.path.splitext(item)[1] != '.json']
                    if len(possible_originals) != 1:
                        raise RuntimeError(
                            'Ambiguous match: %s', possible_originals)
                    original_id = image_id(db, possible_originals[0])
                    c = db.cursor()
                    c.execute(
                        'INSERT INTO ImageRelations VALUES (?, ?, ?)', [
                            edited_id, original_id, 2])
    db.commit()
    db.close()

# Usage: ./group_version.py <digikam_dir>
if __name__ == '__main__':
    run(sys.argv[1])
