#!/usr/bin/python
#-*- coding:utf-8-*-
#code by HAWK.Li

import os
import time
import sitecustomize

def version(cmds,cmd):
    """updateself_version : 1.5_2012-3-12_Release
    """
    return version.__doc__


if __name__ == '__main__':
    """此方法用于杀掉正在运行的CMDServer进程，并将更新包中的新程序进行覆盖
    此模块的设计不合理，大规模使用会出现更新失败的可能，需要考虑重构
    """
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
