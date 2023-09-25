#!/usr/bin/python3

# pjscicalc: a scientific calculator in python/html/javascript
# Copyright (C) 2021–3 John D Lamb
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

import sys 
import os 
import PObject
import re
import mpmath

import calculator

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QSizePolicy
#from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor

class WebPage(QWebEngineView):
    def __init__(self,app,parent):
        self.app = app
        self.parent = parent
        QWebEngineView.__init__(self)
        self.titleChanged.connect(self._on_title_change)

    def _on_title_change(self):
        update(self)
        pass

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
  #print('update')
  global scale
  global memory
  global answer
  #print("M",memory)
  st = e.title()
  #print(st)
  if '?' == st:
    #print('Copyleft')
    dlg = QMessageBox()
    dlg.setIcon(QMessageBox.Information)
    dlg.setText('''
    Copyright © 2021–3 John D Lamb
    
    This program is free software: you can redistribute it and/
    or modify it under the terms of the GNU General Public
    License as published by the Free Software Foundation,
    either version 3 of the License, or (at your option) any
    later version.
    
    This program is distributed in the hope that it will be
    useful, but WITHOUT ANY WARRANTY; without even the
    implied warranty of MERCHANTABILITY or FITNESS FOR A
    PARTICULAR PURPOSE.  See the GNU General Public
    License for more details.
    
    You should have received a copy of the GNU General
    Public License along with this program.  If not, see
    <https://www.gnu.org/licenses/>.
    ''')
    dlg.setWindowTitle('Copyright notice')
    dlg.setStandardButtons(QMessageBox.Ok)
    dlg.exec_()
    script = 'document.title = "!";'
    browser.page().runJavaScript(script)  
  elif 'fullscreen' == st:
    screen = e.app.primaryScreen()
    size = e.parent.size()
    rect = screen.availableGeometry()
    if size.width() >= rect.width()-1 or size.height() == rect.height():
      # Guess it is full screen
      e.parent.resize(800,400)
    else:
      # try to make full screen
      if rect.width() >= 2 * rect.height():
        # work with rect.height
        e.parent.resize(2*rect.height(),rect.height())
      else:
        # More likely work with width
        h = int(rect.width()/2)
        w = h*2
        e.parent.resize(w,h)
    script = 'document.title = "!";'
    browser.page().runJavaScript(script)  
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
    browser.page().runJavaScript(script)  
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
    browser.page().runJavaScript(script)  
  else:
    plist = []
    if 'about:blank' != st:
       plist = PObject.convertStringToPObjectList(st,memory,answer)
    else:
       return
    if 0 != len(plist):
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
    browser.page().runJavaScript('document.getElementById("output-panel").innerHTML="'+output+'";')
    script = 'document.title = "!";' # in case expression started with ANS;
    browser.page().runJavaScript(script) 
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
      browser.page().runJavaScript(script)
  
if __name__ == "__main__":
    app = QApplication([])
    # And a window
    win = QWidget()
    win.setWindowTitle('Scientific calculator')
    browser = WebPage(app,win)
    
    # And give it a layout
    layout = QVBoxLayout()
    win.setLayout(layout)
    win.resize(800,400)

    # Create and fill a QWebView
    browser.setHtml(html_string)
    layout.setContentsMargins(0,0,0,0)
    layout.addWidget(browser)
    win.show()
    sys.exit(app.exec_())  # only need one app, one running event loop
