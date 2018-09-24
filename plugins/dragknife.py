#!/usr/bin/python
# -*- coding: ascii -*-

# Author: @harvie Tomas Mudrunka
# Date: 25 sept 2018

__author__ = "@harvie Tomas Mudrunka"
#__email__  = ""

__name__ = _("DragKnife")
__version__ = "0.1"

import math
import os.path
import re
from CNC import CNC,Block
from bpath import eq, Path, Segment
from ToolsPage import Plugin
from math import pi, sqrt, sin, cos, asin, acos, atan2, hypot, degrees, radians, copysign, fmod

class Tool(Plugin):
	__doc__ = _("""Drag knife postprocessor""")			#<<< This comment will be show as tooltip for the ribbon button
	def __init__(self, master):
		Plugin.__init__(self, master,"DragKnife")
		self.icon = "dragknife"			#<<< This is the name of file used as icon for the ribbon button. It will be search in the "icons" subfolder
		self.group = "CAM"	#<<< This is the name of group that plugin belongs
		#self.oneshot = True
		#Here we are creating the widgets presented to the user inside the plugin
		#Name, Type , Default value, Description
		self.variables = [			#<<< Define a list of components for the GUI
			("name"    ,    "db" ,    "", _("Name")),							#used to store plugin settings in the internal database
			("offset", "mm", "3", _("dragknife offset"))
		]
		self.buttons.append("exe")  #<<< This is the button added at bottom to call the execute method below


	# ----------------------------------------------------------------------
	# This method is executed when user presses the plugin execute button
	# ----------------------------------------------------------------------
	def execute(self, app):
		dragoff = self.fromMm("offset")

		#print("go!")
		blocks  = []
		for bid in app.editor.getSelectedBlocks():
			if len(app.gcode.toPath(bid)) < 1: continue

			#nblock = Block("flat "+app.gcode[bid].name())
			#for i in app.gcode[bid]:
			#	nblock.append(re.sub(r"\s?z-?[0-9\.]+","",i))
			#blocks.append(nblock)

			eblock = Block("drag "+app.gcode[bid].name())
			opath = app.gcode.toPath(bid)[0]
			npath = Path("dragknife "+app.gcode[bid].name())
			for i,seg in enumerate(opath):
				npath.append(seg)
				overcut = seg.B+(seg.tangentStart()*dragoff)
				npath.append(Segment(Segment.LINE, seg.B, overcut))
				if len(opath) > i+1:
					next = opath[i+1]
					arca = Segment(Segment.CW, overcut, next.distPoint(dragoff))
					arca.setCenter(seg.B)
					arcb = Segment(Segment.CCW, overcut, next.distPoint(dragoff))
					arcb.setCenter(seg.B)
					if arca.length() < arcb.length():
						npath.append(arca)
					else:
						npath.append(arcb)

			eblock = app.gcode.fromPath(npath,eblock)
			blocks.append(eblock)



		#active = app.activeBlock()
		#if active == 0: active+=1
		active=-1 #add to end
		app.gcode.insBlocks(active, blocks, "Dragknife") #<<< insert blocks over active block in the editor
		app.refresh()                                                                                           #<<< refresh editor
		app.setStatus(_("Generated: Dragknife"))                           #<<< feed back result
		#app.gcode.blocks.append(block)