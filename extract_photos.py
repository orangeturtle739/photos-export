#! /usr/bin/env python3

import sys
import os
import sqlite3
import hashlib
import json
import progressbar
import uuid
import shutil
from libxmp import XMPFiles


def run(lib_dir, output_dir):
    db_path = os.path.join(lib_dir, 'database')
    main_db_path = os.path.join(db_path, 'Library.apdb')
    proxy_db_path = os.path.join(db_path, 'ImageProxies.apdb')
    edited_root = os.path.join(lib_dir, 'resources', 'modelresources')
    edited_index = {}
    for subdir, dirs, files in os.walk(edited_root):
        for f in files:
            images = os.listdir(subdir)
            if len(images) != 1:
                print('Error! "%s" should contain 1 image.', images)
            edited_index[
                os.path.basename(subdir)] = os.path.join(
                subdir, images[0])

    main_db = sqlite3.connect(main_db_path)
    main_db.row_factory = sqlite3.Row
    proxy_db = sqlite3.connect(proxy_db_path)
    proxy_db.row_factory = sqlite3.Row

    c = main_db.cursor()
    c.execute('SELECT COUNT(*) from RKMaster')
    (number_of_rows,) = c.fetchone()
    c.execute('SELECT * FROM RKMaster')
    count = 0
    bar = progressbar.ProgressBar(max_value=number_of_rows)
    for master in bar(iter(c.fetchone, None)):
        master_uuid = master['uuid']
        master_path = os.path.join(lib_dir, 'Masters', master['imagePath'])
        latitude = None
        longitude = None
        master_albums = set([])
        master_keywords = set([])
        master_rating = None
        vc = main_db.cursor()
        vc.execute('SELECT * FROM RKVersion WHERE masterUuid=?', [master_uuid])
        edited_paths = []
        unadjusted_count = 0
        for version in iter(vc.fetchone, None):
            edited_path = []
            is_master = False
            if version['adjustmentUuid'] != 'UNADJUSTEDNONRAW':
                ac = proxy_db.cursor()
                ac.execute('SELECT * FROM RKModelResource WHERE resourceTag=?',
                           [version['adjustmentUuid']])
                for resource in iter(ac.fetchone, None):
                    if resource['attachedModelType'] == 2 and resource[
                            'resourceType'] == 4:
                        if len(edited_path) != 0:
                            pass
                            # print("Warning! Multiple valid edits!")
                        edited_path += [edited_index[resource['resourceUuid']]]
            else:
                unadjusted_count += 1
                is_master = True

            new_latitude = version['latitude']
            new_longitude = version['longitude']
            if latitude is None or longitude is None:
                latitude = new_latitude
                longitude = new_longitude
            elif abs((new_latitude or 100000) - latitude) > 0.00001 and abs((new_longitude or 100000) - longitude) > 0.00001:
                print("Inconsistent location: (%f, %f) -> (%f, %f)" %
                      (latitude, longitude, new_latitude, new_longitude))

            kc = main_db.cursor()
            kc.execute('SELECT * FROM RKAlbumVersion WHERE versionId=?',
                       [version['modelId']])
            albums = set([])
            for album_id in iter(kc.fetchone, None):
                alc = main_db.cursor()
                alc.execute('SELECT * FROM RKAlbum WHERE modelId=?',
                            [album_id['albumId']])
                r_albums = alc.fetchall()
                if len(r_albums) != 0:
                    if len(r_albums) != 1:
                        print(
                            "Warning! More than one album for ID %d" %
                            album_id['albumId'])
                    albums |= set([r_albums[0]['name']])

            wc = main_db.cursor()
            wc.execute(
                'SELECT * FROM RKKeywordForVersion WHERE versionId=?', [version['modelId']])
            keywords = set([])
            for keyword_id in iter(kc.fetchone, None):
                klc = main_db.cursor()
                klc.execute('SELECT * FROM RKKeyword WHERE modelId=?',
                            [keyword_id['keywordId']])
                r_keyword = klc.fetchall()
                if len(r_keyword) != 0:
                    if len(r_keyword) != 1:
                        print(
                            "Warning! More than one keyword for ID %d" %
                            keyword_id['keywordId'])
                    keywords |= set([r_keyword[0]['name']])

            rating = version['mainRating']
            if is_master:
                master_albums |= albums
                master_keywords |= keywords
                master_rating = rating
            else:
                for foo in edited_path:
                    iuuid = '%s_%010d' % count
                    count += 1
                    edited_paths += [{'path': foo,
                                      'albums': list(albums),
                                      'keywords': list(keywords),
                                      'rating': rating,
                                      'uuid': iuuid,
                                      'in_library': True}]

        master_in_library = (unadjusted_count != 0)
        iuuid = '%s_%010d' % count
        count += 1

        base_data = {'latitude': latitude, 'longitude': longitude}
        master_data = {
            'uuid': iuuid,
            'path': master_path,
            'in_library': master_in_library,
            'albums': list(master_albums),
            'keywords': list(master_keywords),
            'rating': master_rating}
        # print(dict(base_data, **master_data))
        # print(edited_paths)
        if unadjusted_count != 0 and unadjusted_count != 1:
            # print("Warning! %d unadjusted images!" % unadjusted_count)
            pass

        # Export!
        base_export_path = os.path.join(output_dir, iuuid)
        # Hard link the master
        shutil.copy2(
            master_path,
            os.path.join(
                output_dir,
                iuuid +
                os.path.splitext(master_path)[1].lower()))
        # Write the data
        with open(os.path.join(output_dir, '%s.json' % iuuid), 'w') as log_file:
            print(
                json.dumps(
                    dict(
                        dict(
                            base_data,
                            **master_data),
                        derived_from=None)),
                file=log_file)
        # Hard link the edits
        edit_export_path = os.path.join(base_export_path, 'edited')
        for edit_info in edited_paths:
            shutil.copy2(
                edit_info['path'],
                os.path.join(
                    output_dir,
                    '%s%s' %
                    (edit_info['uuid'],
                     os.path.splitext(
                        edit_info['path'])[1].lower())))
            with open(os.path.join(output_dir, '%s.json' % edit_info['uuid']), 'w') as log_file:
                print(
                    json.dumps(
                        dict(
                            dict(
                                base_data,
                                **edit_info),
                            derived_from=iuuid)),
                    file=log_file)

if __name__ == '__main__':
    run(sys.argv[1], sys.argv[2])
