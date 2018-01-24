import zipfile, os

def zipdir(path, extension, zip):
    for each in os.listdir(path):

        if each.endswith('.xml'):

            try:
                zip.write(path + each)

            except IOError:
                None

if __name__ == '__main__':
    zip = zipfile.ZipFile('Python3.zip', 'w')
    zipdir('bootstrap', '.xml', zip)
    zip.close()