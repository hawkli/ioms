
from distutils.core import setup
import glob,sys
import wx
import py2exe
import sitecustomize
reload(sys)
sys.setdefaultencoding('utf-8')

setup(
      options={'py2exe': {'bundle_files': 1,
                        'optimize': 2,
                        'compressed': 1}},
    zipfile=None,
    windows=["IOMSUI.py"],
    data_files=[("img",glob.glob("img\\*")),("data",glob.glob("data\\*"))]
    )

