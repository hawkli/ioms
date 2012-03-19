#!/usr/bin/python
#-*- coding:utf-8-*-
#code by HAWK.Li

def version(cmds,cmd):
    """gridModel_version : 1.5_2012-03-12_Release
    """
    return version.__doc__


import  wx
import  wx.grid as gridlib
import time
class CustomDataTable(gridlib.PyGridTableBase):
    def __init__(self,colLabels,dataTypes,data):
        gridlib.PyGridTableBase.__init__(self)
        self.colLabels = colLabels
        self.dataTypes = dataTypes
        self.data = data
    def GetNumberRows(self):
        return len(self.data)
    def GetNumberCols(self):
        return len(self.data[0])
    def IsEmptyCell(self, row, col):
        return False
    def GetValue(self, row, col):
        try:
            return self.data[row][col]
        except IndexError:
            return ''
    def SetValue(self, row, col, value):
        try:
            self.data[row][col] = value
        except:
            wx.MessageBox(u"赋值未结束",u"集中运维管理系统",wx.OK|wx.ICON_ERROR)
    def GetColLabelValue(self, col):
        return self.colLabels[col]
    def GetTypeName(self, row, col):
        return self.dataTypes[col]
    def CanGetValueAs(self, row, col, typeName):
        colType = self.dataTypes[col].split(':')[0]
        if typeName == colType:
            return True
        else:
            return False
    def CanSetValueAs(self, row, col, typeName):
        return self.CanGetValueAs(row, col, typeName)
      
class CustTableGrid(gridlib.Grid):
    def __init__(self, parent, colLabels,dataTypes,data,state,pos=0):
        gridlib.Grid.__init__(self, parent, -1,size=(100,800))
        table = CustomDataTable(colLabels,dataTypes,data)
        self.SetTable(table, True)
        self.SetRowLabelSize(0)
        self.SetMargins(0,0)
        #不可修改，防止点击报内存错误
        for i in range(self.GetNumberRows()):
            for j in range(0,self.GetNumberCols()):
                self.SetReadOnly(i,j)
                self.SetCellAlignment(i,j,wx.CENTER,wx.CENTER)
            self.SetRowSize(i,20)
        
        self.AutoSizeColumns(False)
        if state:
            self.StateDefine(data,pos)
        else:
            pass
    def SetData(self,colLabels,dataTypes,data,state,pos=0):
        table = CustomDataTable(colLabels,dataTypes,data)
        self.SetTable(table, True)
        self.AutoSizeColumns(False)
        if state:
            self.StateDefine(data,pos)
        else:
            pass
    def StateDefine(self,data,pos):
        for item in data:
            if item[pos]==' ':
                pass
            else:
                font = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, 'gbk')
                #font.SetPointSize(20)
                now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                tem_time1 = time.mktime(time.strptime(item[pos],"%Y-%m-%d %H:%M:%S"))
                tem_time2 = time.mktime(time.strptime(now_time,"%Y-%m-%d %H:%M:%S"))
                #消息发送时间大于三分钟的，状态为黑色
                self.SetCellFont(data.index(item),pos,font)
                if tem_time2-tem_time1 >= 180.0 :
                    item[pos] = u"●"
                    self.SetCellTextColour(data.index(item),pos,"black")
                else:
                    item[pos] = u"●"
                    self.SetCellTextColour(data.index(item),pos,"green")
        self.AutoSizeColumns(False)