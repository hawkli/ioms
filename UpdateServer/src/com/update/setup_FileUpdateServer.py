
from distutils.core import setup
import py2exe

setup(
    options={'py2exe': {'bundle_files': 1,
                        'optimize': 2,
                        'compressed': 1}},
    zipfile=None,
    console=["FileUpdateServer.py"],
    data_files=["key.ini",("conf",["conf/AUServer.ini", "conf/file.xml"])])

