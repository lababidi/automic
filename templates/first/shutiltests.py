
from shutil import make_archive
import os

archive_name = os.path.expanduser(os.path.join('~', 'PycharmProjects/untitled/templates/bootstrap-archive'))
root_dir = os.path.expanduser(os.path.join('~', 'PycharmProjects/untitled/templates/bootstrap'))
make_archive(archive_name, 'zip', root_dir)

