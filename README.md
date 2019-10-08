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
* Folder and Album structure (photos not included in any album will be placed on ROOT of destination directory)

The program writes as much metadata as it can directly into the images using EXIF. (See http://www.sno.phy.queensu.ca/~phil/exiftool/TagNames/XMP.html for information about supported tags.)
This program worked on the database format around 2019-07, Apple Photos version 4.0 (also tested in a Apple Photos 3.0 with about 100.000 photos).

The program operates in distinct phases, which can all be run independently:

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
  $ ./group_versions.py <digikam_db_dir> <photos_dir>
  ```
* Folder Structure: Reads Library Database and generates a file (folders.json) with all information necessary to replicate the folder structure contained in Photos.app. Place the destination file within the output directory with exported photos. Run as:
  ```shell
  $ ./folder_structure.py <library_dir> <output_dir>
  ```

* Albums Data: Reads Library Database and generates a file (albums.json) with all information necessary to place the album inside the right folder. Place the destination file within the output directory with exported photos. Run as:
  ```shell
  $ ./albums_data.py <library_dir> <output_dir>
  ```

* Album folders: copy/move all photo's in folders according to the albums they are in. If a photo is in two different albums, it will be copied in two different folders, each folder with the name of the album. Run as:
  ```shell
  $ ./album_folder.py <source_dir> <output_dir>
  ```

To run all the phases together (except for group photos), run:

```shell
$ ./photos_export.py <foo.photoslibrary> <output_dir>
```

All the scripts have nice progress bars.

## Contributing
If you find a bug, or there is something you would like added, your best bet is to try to patch it yourself and open a pull request. I don't have many photos libraries to test on, so your library is probably the only way to test.
