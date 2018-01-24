import os
import zipfile
from io import BytesIO

memory_file = BytesIO()
with zipfile.ZipFile(memory_file, 'w') as zf:
    files = zf
    for individualFile in files:
        data = zipfile.ZipInfo(individualFile['fileName'])
        data.date_time = time.localtime(time.time())[:6]
        data.compress_type = zipfile.ZIP_DEFLATED
        zf.writestr(data, individualFile['fileData'])

memory_file.seek(0)


##    memory_file = BytesIO()
#    zf = zipfile.ZipFile("bootstrap-archive.zip", "w")
#    for dirname, subdirs, files in os.walk("templates/bootstrap"):
#        zf.write("bootstrap-archive.zip")
#        for filename in files:
#            zf.write(os.path.join(dirname, filename))
#    zf.close()