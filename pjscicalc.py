#!/usr/bin/python3

# pjscicalc: a scientific calculator in python/html/javascript
# Copyright (C) 2021 John D Lamb
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import wx
import wx.html2
import os 
import PObject
import re
import mpmath

import calculator

class MyBrowser(wx.Frame): 
  def __init__(self, *args, **kwds): 
    wx.Frame.__init__(self, *args, **kwds) 
    sizer = wx.BoxSizer(wx.VERTICAL) 
    self.browser = wx.html2.WebView.New(self) 
    self.SetMinSize((600,336))
    sizer.Add(self.browser, 1, wx.EXPAND, 10) 
    self.SetSizer(sizer) 
    self.SetSize((800,436)) 
    self.Bind(wx.html2.EVT_WEBVIEW_ERROR,self.on_webview_error)

  def on_webview_error(self,event):
    print(event)
    print(event.GetURL())

# html string to display in WebView widget
dir_path = os.path.dirname(os.path.realpath(__file__))
fname = os.path.join(dir_path,'calculator.html')
html_string = calculator.calculator(fname)

# Global variables
RADIAN_SCALE = 1.0
DEGREE_SCALE = mpmath.pi/180.0
scale = DEGREE_SCALE

memory = mpmath.mpf(0)
answer = mpmath.mpf(0)

def update(e):
  print('update')
  global scale
  global memory
  global answer
  #print("M",memory)
  st = e.GetString()
  print(st)
  if '?' == st:
    #print('Copyleft')
    dlg = wx.MessageDialog(browser, '''
    Copyright © 2021 John D Lamb
    
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
    ''', caption='Copyright notice', style=wx.OK)
    dlg.ShowModal()
    dlg.Destroy()
    script = 'document.title = "!";'
    browser.browser.RunScript(script)  
  elif '!' == st:
    pass # explicit do nothing
  elif 'MCL;' == st:
    memory = mpmath.mpf(0)
    script  = 'var label = document.getElementById("display-extra");\n'
    script += 'var str = "";\n'
    script += 'str += "&emsp;";\n'
    script += 'str += "&nbsp;";\n'
    if RADIAN_SCALE == scale:
      script += 'str += "radians";\n'
    else:
      script += 'str += "degrees";\n'
    script += "label.innerHTML = str;\n"
    browser.browser.RunScript(script)  
  elif 'd' == st or 'r' == st:
    if 'd' == st:
      scale = DEGREE_SCALE
    elif 'r' == st:
      scale = RADIAN_SCALE
    script  = 'var label = document.getElementById("display-extra");\n'
    script += 'var str = "";\n'
    #print('M',memory,type(memory))
    if memory == 0:
      script += 'str += "&emsp;";\n'
    else:
      script += 'str += "M";\n'
    script += 'str += "&nbsp;";\n'
    if RADIAN_SCALE == scale:
      script += 'str += "radians";\n'
    else:
      script += 'str += "degrees";\n'
    script += "label.innerHTML = str;\n"
    browser.browser.RunScript(script)  
  else:
    plist = PObject.convertStringToPObjectList(st,memory,answer)
    if isinstance(plist[0],PObject.Sto):
      #print("l",len(plist))
      plist = plist[1:len(plist)]
      store = 1 # 1 STO, 2 M+ 3 M- 4 MCL
      #print('store set to',store)
    elif isinstance(plist[0],PObject.Mplus):
      #print("l",len(plist))
      plist = plist[1:len(plist)]
      store = 2 # 1 STO, 2 M+ 3 M- 4 MCL
      #print('store set to',store)
    elif isinstance(plist[0],PObject.Mminus):
      #print("l",len(plist))
      plist = plist[1:len(plist)]
      store = 3 # 1 STO, 2 M+ 3 M- 4 MCL
    elif isinstance(plist[0],PObject.Mcl):
      # Not used
      #print("l",len(plist))
      plist = plist[1:len(plist)]
      store = 4 # 1 STO, 2 M+ 3 M- 4 MCL
    else:
      store = 0
      #print('store set to',store)
    value,output = PObject.evaluate(plist,scale)
    #print('@ ',plist,value,output)
    if output != 'Error':
      error = False
      answer = value
      #print("A",answer)
    else:
      error = True
    browser.browser.RunScript('document.getElementById("output-panel").innerHTML="'+output+'";')
    script = 'document.title = "!";' # in case expression started with ANS;
    browser.browser.RunScript(script) 
    ## may have to store result
    #print('store =',store,error)
    if store > 0 and not error:
      if 1 == store:
        memory = value # we calculate answer as soon as STO is pressed.
      elif 2 == store:
        memory += value # we calculate answer as soon as M+ is pressed.
      else: # assume 3 == store: 
        memory -= value # we calculate answer as soon as M– is pressed.
      script  = 'var label = document.getElementById("display-extra");\n'
      script += 'var str = "";\n'
      #print('M',memory,type(memory))
      if memory == 0:
        script += 'str += "&emsp;";\n'
      else:
        script += 'str += "M";\n'
      script += 'str += "&nbsp;";\n'
      if RADIAN_SCALE == scale:
        script += 'str += "radians";\n'
      else:
        script += 'str += "degrees";\n'
      script += "label.innerHTML = str;\n"
      browser.browser.RunScript(script)
  
if __name__ == '__main__': 
  app = wx.App() 
  browser = MyBrowser(None, -1,title='Scientific calculator') 
  browser.Bind(wx.html2.EVT_WEBVIEW_TITLE_CHANGED, update)
  browser.browser.SetPage(html_string,"")
  browser.Show() 
  app.MainLoop() 

