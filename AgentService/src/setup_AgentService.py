from distutils.core import setup
import sys
import string
import threading
import time
import subprocess
import re
import csv
import os
import win32serviceutil
import win32service
import win32event
import py2exe

##sys.argv.append('py2exe')

setup(
    version="1.0",
    description="AgentService", 
    name="AgentService",
    options={'py2exe': {'bundle_files': 1,
                        'optimize': 2,
                        'compressed': 1}},
    service=["AgentService"],
    data_files=[("",["agent.ini","crontab.ini","auto.ini","key.ini"])],
    zipfile=None
)
