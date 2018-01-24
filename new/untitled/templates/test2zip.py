import zipfile, os
def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))

if __name__ == '__main__':
    zipf = zipfile.ZipFile('Python1.zip', 'w', zipfile.ZIP_DEFLATED)
    zipdir('templates/bootstrap', zipf)
    zipf.close()