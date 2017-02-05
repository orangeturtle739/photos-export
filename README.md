# Photos Export
A collection of python scripts to export photos from an Apple Photos database while preserving metadata and edits.

## Disclaimer
While I tested this carefully with my photo library, as stated in [the license](LICENSE.txt):
> This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should make sure you have a backup of your photo library **before** doing _anything_, otherwise assume that you will _lose everything_!

## Dependencies

* `progressbar`: `pip install progressbar`
* `pyexiftool`: https://github.com/smarnach/pyexiftool

## Usage
This program takes an Apple Photos (_not_ iPhoto) database and exports all the
pictures in it while preserving:

* GPS location data
* Albums (as tags)
* Keywords (as tags)
* Ratings
* Edits (exports the original and all edits for each image)

This program worked on the database format around 2016-08. Apple has since changed the naming of some files, and this script no longer works, though it might with some small fixes. I do not have access to the new format, so I can't test it. However, feel free to update it and open a pull request!

The program is operated into distinct phases, which can all be run independently:

* Extraction: the program reads the Photos database, and copies all the files and metadata to a new folder. All the metadata is stored in JSON sidecar files. Done in [`extract_photos.py`](extract_photos.py). Run as:
  ```shell
  $ ./extract_photos.py <foo.photoslibrary> <output_dir>
  ```
* Clean albums: lots of my albums were simply dates. I didn't like that because that didn't add much information; each photo had a date already. The [`clean_albums.py`](clean_albums.py) processes all the JSON sidecar files created during the extraction process and removes any albums that are only a date. Run as:
  ```shell
  $ ./clean_albums.py <output_dir>
  ```
* Set EXIF: copies all the data from the JSON sidecar files into the EXIF fields of the image. Run as:
  ```shell
  $ ./set_exif.py <output_dir>
  ```
* Group versions: the script is digikam specific. Before running this script, import the photos into digikam. Launch digikam at least once, then close it. Then, run this script to write all the photo version and edit information into digikam's database so digikam can group edited photos.
Run as:
  ```shell
  $ ./group_versions.py <output_dir>
  ```

To run all the phases together (except for group photos), run:
```shell
$ ./photos_export.py <foo.photoslibrary> <output_dir>
```

All the scripts have nice progress bars.

## Contributing
If you find any bug, or there is something you would like added, your best bet is to try to patch it yourself and open a pull request. I don't have many photos libraries to test on, so your library is probably the only way to test.
