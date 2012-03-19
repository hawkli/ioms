#!/usr/bin/python
#-*- coding:utf-8-*-
#code by HAWK.Li

import os
import sys
import wx
reload(sys)
sys.setdefaultencoding('utf-8')

ID_OPEN = 101
ID_EXIT = 110
ID_SAVE = 111
ID_BUTTON = 112
ID_SAVEAS = 113
ID_ABOUT = 120

def version(cmds,cmd):
    """wxTextEditor_version : 1.5_2012-3-12_Release
    """
    return version.__doc__

class MainWindow(wx.Frame):
    """ We simply derive a new class of Frame. """
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(500,100))
        self.control = wx.TextCtrl(self, 1, style=wx.TE_MULTILINE)
        self.CreateStatusBar()
        filemenu  = wx.Menu()
        filemenu.Append(ID_OPEN,u"打开文件","open file")
        #filemenu.AppendSeparator()
        filemenu.Append(ID_SAVE,u"保存文件"," save file")
        #filemenu.AppendSeparator()
        filemenu.Append(ID_SAVEAS,u"另存为..."," save as ...")
        filemenu.AppendSeparator()
        filemenu.Append(ID_EXIT,u"退出","exit")
        filemenu1  = wx.Menu()
        filemenu1.Append(ID_ABOUT,u"关于","about")        
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,u"文件")
        menuBar.Append(filemenu1,u"帮助")        
        self.SetMenuBar(menuBar)
        wx.EVT_MENU(self,ID_OPEN,self.open)
        wx.EVT_MENU(self,ID_EXIT,self.exit)
        wx.EVT_MENU(self,ID_SAVEAS,self.SaveAs)
        wx.EVT_MENU(self,ID_SAVE,self.save)
        wx.EVT_MENU(self,ID_ABOUT,self.SystemAbout)        
        self.sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        self.buttons = []
        
#        for i in range(0,6):
#            self.buttons.append(wx.Button(self,ID_BUTTON+i,"Button &"+'i'))    
#            self.sizer2.Add(self.buttons[i],1,wx.EXPAND)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.control,1,wx.EXPAND)
        self.sizer.Add(self.sizer2,0,wx.EXPAND)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        self.sizer.Fit(self)
        self.SetMinSize(wx.Size(400, 300))
        self.SetSize(wx.Size(800,600))
        self.Show(True)
        
    def readtxt(self,txt):        
        self.control.SetValue(txt)
        
    def exit(self,e):
        '''用户退出窗口'''
        self.Close(True)
        
    def open(self,e):
        '''打开文件 '''
        self.dirname = ''
        dlg = wx.FileDialog(self,u"选择打开一个文件",self.dirname,"","*.*",wx.OPEN)
        
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            f = open(os.path.join(self.dirname,self.filename),'r')
            self.control.SetValue(f.read())
            f.close()
        dlg.Destroy()
        
    def save(self,e):
        '''保存文件'''
        try:
            f = open(os.path.join(self.dirname,self.filename),'w')
            try:
                content = self.control.GetValue()
                f.write(content)
            except UnboundLocalError:
                wx.MessageBox(u"文件不存在！",u"警告",style=wx.OK|wx.ICON_EXCLAMATION)
                #sys.exit(0)
            finally:
                f.close()
        except AttributeError:
            wx.MessageBox(u"文件不存在！",u"警告",style=wx.OK|wx.ICON_EXCLAMATION)
            #sys.exit(0)

    def SaveAs(self,e):
        '''另存为的方法'''
        self.dirname = ''
        dlg = wx.FileDialog(self, u"另存为……", self.dirname, "", "*.log", wx.SAVE | wx.OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            itcontains = self.control.GetValue()

            self.filename=dlg.GetFilename()
            self.dirname=dlg.GetDirectory()
            filehandle=open(os.path.join(self.dirname, self.filename),'w')
            filehandle.write(itcontains)
            filehandle.close()
        dlg.Destroy()

    def SystemAbout(self,event):
        """本程序仿WINDOWS的记事本，\n
用于输出结果或日志文件的收集。\n
        """
        if hasattr(sys, "frozen") and getattr(sys, "frozen") == "windows_exe": 
            helpText = u"本程序用于输出结果或日志文件的收集。\n版本号: 1.00"
        else:
            helpText =self.SystemAbout.__doc__ + version(0,0)
        wx.MessageBox(helpText,u"关于本程序：",style=wx.OK|wx.ICON_EXCLAMATION)
        #event.Skip()            

if __name__ == "__main__":                    
    txt = "hellworld"    
    app = wx.PySimpleApp()
    frame=MainWindow(None,-1, u'输出日志收集记事本')
    frame.readtxt(txt)
    app.MainLoop()