import zipfile
import shutil
import datetime
import glob
import os

src_loc = "templates/bootstrap"
archive_loc = "/Users/miclark/PycharmProjects/untitled/templates/"
zip_file_name = "Python1.zip"



zf = zipfile.ZipFile(os.path.join(archive_loc,zip_file_name),"w")

for dirname,subdirs,files in os.walk(os.path.abspath(src_loc)):
    zf.write(dirname)
    for filename in files:
        name, ext = os.path.splitext(filename)
        zf.write(os.path.join(dirname,filename))
zf.close()

