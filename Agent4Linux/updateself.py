#!/usr/bin/python
#-*- coding:utf-8-*-

import os
import time
import sitecustomize

def version(cmds,cmd):
    """updateself_version : 1.10_2011-02-16_ALPHA
    """
    return version.__doc__


if __name__ == '__main__':
    try:
        time.sleep(3)
        print "kill CMDServer..."
        str = os.popen('taskkill /IM CMDServer.exe /F').readlines()
        for s in str:
            print s
    except:
        print "kill CMDServer.exe Error!"
        
    time.sleep(3)
    try:
        print "remove CMDServer..."
        os.remove('CMDServer.exe')
        print "remove CMDServer OK, rename begin..."
    except:
        print "remove CMDServer.exe Error!"
    try:
        os.rename('CMDServer.exe_', 'CMDServer.exe')
    except:
        print "rename CMDServer.exe Error!"
    
    print "updateself Over."
