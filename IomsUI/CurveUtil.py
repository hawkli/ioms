#!/usr/bin/python
#-*- coding:utf-8-*-
#code by HAWK.Li

import wx

def version(cmds,cmd):
    """CurveUtil_version : 1.5_2012-3-12_Release
    """
    return version.__doc__

class LineChart(wx.Panel):
    def __init__(self, parent, data, topTitle, xtitle, ytitle):
        self.data = data
        self.topTitle = topTitle
        self.xtitle = xtitle
        self.ytitle = ytitle
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour('WHITE')

        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        dc.SetDeviceOrigin(40, 240)
        dc.SetAxisOrientation(True, True)
        dc.SetPen(wx.Pen('WHITE'))
        dc.DrawRectangle(1, 1, 300, 200)
        self.DrawAxis(dc)
        self.DrawGrid(dc)
        self.DrawTitle(dc)
        self.DrawData(dc)

    def DrawAxis(self, dc):
        dc.SetPen(wx.Pen('#0AB1FF'))
        font =  dc.GetFont()
        font.SetPointSize(8)
        dc.SetFont(font)
        dc.DrawLine(1, 1, 500, 1)
        dc.DrawLine(1, 1, 1, 201)

        for i in self.ytitle:
            dc.DrawText(str(i), -30, i*2+5)
            dc.DrawLine(2, i*2, -5, i*2)

        for i in range(100, 300, 100):
            dc.DrawLine(i, 2, i, -5)
            
        xtitlelen = len(self.xtitle)
        xtitlewidth = 480//xtitlelen
        for i in range(xtitlelen):
            dc.DrawText(self.xtitle[i], i*xtitlewidth+xtitlewidth//2//2, -10)

    def DrawGrid(self, dc):
        dc.SetPen(wx.Pen('#d5d5d5'))

        for i in range(20, 220, 20):
            dc.DrawLine(2, i, 500, i)

        for i in range(100, 500, 100):
            dc.DrawLine(i, 2, i, 200)

    def DrawTitle(self, dc):
        font =  dc.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        dc.SetFont(font)
        dc.DrawText(self.topTitle, 200, 235)


    def DrawData(self, dc):
        penWidth = 500//len(self.data)
        dc.SetPen(wx.Pen('#0ab1ff', 1))
        j = 0
        for _data in self.data:
            for i in range(penWidth):
                dc.DrawLine(j * penWidth+i, 2, j * penWidth+i, _data[1]*2)
            j = j + 1


class LineChartExample(wx.Frame):
    def __init__(self, parent, id, title, data, topTitle):
        wx.Frame.__init__(self, parent, id, title, size=(590, 500))

        panel = wx.Panel(self, -1)
        panel.SetBackgroundColour('WHITE')

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        
        xtitle = ('00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23')
        ytitle = (10, 20, 30, 40, 50, 60, 70, 80, 90, 100)

        linechart = LineChart(panel, data, topTitle, xtitle, ytitle)
        hbox.Add(linechart, 1, wx.EXPAND | wx.ALL, 15)
        panel.SetSizer(hbox)

        self.Centre()
        self.Show(True)

if __name__ == "__main__":
    
    data = ((10, 9), (20, 22), (30, 21), (40, 30), (50, 41),
            (60, 53), (70, 45), (80, 20), (90, 19), (100, 22),
            (110, 42), (120, 62), (130, 43), (140, 71), (150, 89),
            (160, 65), (170, 126), (180, 187), (190, 128), (200, 125),
            (210, 150), (220, 129), (230, 133), (240, 134), (250, 165),
            (260, 132), (270, 130), (280, 159), (290, 163), (300, 94))
    data1 = []
    for i in range(24):
        data1.append([i*20, 0])
    data1[11][1] = 45 
    print data1
    
    app = wx.App()
    LineChartExample(None, -1, 'A line chart', data1, 'A line chart')
    app.MainLoop()
    