Facebook-Group-Photos-Downloader

Facebook-Group-Photos-Downloader will download all photos from a facebook group to a specified download path in the
config file.
Prior to downloading each new photo, Facebook-Group-Photos-Downloader will verify that the photo does not already
exiast in the download path.
If the photo already exists in the download path, the download will be skipped, and it will move on to the next photo.
If the photo does not already exist in the folder, the photo will be submitted to an image similarity (histogram) function.
The photo will be compared to all photos currently in the download path.
If a duplicate is detected, the location to both photos will be logged to the duplicate-log.txt file.

Requirements*: conda install pillow