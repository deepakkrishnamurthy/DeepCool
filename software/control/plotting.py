import os 
os.environ["QT_API"] = "pyqt5"
import qtpy

import pyqtgraph as pg
import pyqtgraph.dockarea as dock
from pyqtgraph.dockarea.Dock import DockLabel
# import control.utils.dockareaStyle as dstyle


import numpy as np
from collections import deque

# qt libraries
from qtpy.QtCore import *
from qtpy.QtWidgets import *
from qtpy.QtGui import *

from control._def import *
'''
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#                            Plot widget
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
'''

class dockAreaPlot(dock.DockArea):
	def __init__(self, parent=None):
		super().__init__(parent)
		# DockLabel.updateStyle = dstyle.updateStylePatched

		self.plots = {key:PlotWidget(key, self.internal_state) for key in PLOT_VARIABLES.keys()}
		
		self.docks = {key:dock.Dock(key) for key in PLOT_VARIABLES.keys()}

		for key in PLOT_VARIABLES.keys():

			self.docks[key].addWidget(self.plots[key])
		
		# Layout of the plots
		
		self.addDock(self.docks['X'])
		self.addDock(self.docks['Z'],'above',self.docks['X'])

		prev_key = 'Z'
		for key in PLOT_VARIABLES:
			if key not in DEFAULT_PLOTS:
				self.addDock(self.docks[key],'above',self.docks[prev_key])
				prev_key = key

		self.initialise_plot_area()

	def initialise_plot_area(self):

		for key in self.plots.keys():
			self.plots[key].initialise_plot()

	def update_plots(self):
		for key in self.plots.keys():

			self.plots[key].update_plot()


class PlotWidget(pg.GraphicsLayoutWidget):
	def __init__(self,title, data_to_plot, parent=None):
		''' Plots (x,y) data as a lineplot that can be updated at a certain rate.

			Inputs:
				title: What the plot is plotting
				data_to_plot: Individual data streams that are plotted. Each data-stream is plotted as a distinct curve.
			
		'''
		super().__init__(parent)
		self.title=title
		self.data_to_plot = data_to_plot

		
		self.plot_item = self.addPlot(title=title)
		self.plot_item.addLegend()
		self.plot_item.setLabel('left', title, units='C')
		self.plot_item.setLabel('bottom', "Time", units='s')
		self.plot = {}
		
		self.Abscissa = {}
		self.Ordinate = {}
		self.Abs = {}
		self.Ord = {}

		for data in data_to_plot:
			self.Abscissa[data] = deque(maxlen=500)
			self.Ordinate[data] = deque(maxlen=500)
			self.Abs[data] =[]
			self.Ord[data] =[]
			self.plot[data] = self.plot_item.plot(self.Abs[data],self.Ord[data], name = data, fillLevel=0, fillBrush=(255,255,255,30), pen = pg.mkPen(PLOT_COLORS[data], width=3))
			# self.plot[data].setClipToView(True)
		
		self.plot_item.enableAutoRange('xy', True)
		self.plot_item.showGrid(x=True, y=True)
		# self.plot_item.setDownsampling(auto = True)

		
	def update_plot(self, data, x, y):
		''' Update plot using latest data.
			Input: data: 1 x 2 array containing X and Y data
			
		'''
		assert data in self.data_to_plot, "Data stream not in current plot."

		self.Abscissa[data].append(x)
		self.Ordinate[data].append(y)
			
		self.Abs[data] = list(self.Abscissa[data])
		self.Ord[data] = list(self.Ordinate[data])

		self.plot[data].setData(self.Abs[data],self.Ord[data])

	def initialise_plot(self):
		self.Abscissa = {}
		self.Ordinate = {}
		self.Abs = {}
		self.Ord = {}

		self.label = PLOT_UNITS[self.title]

		for data in self.data_to_plot:
			self.Abscissa[data] = deque(maxlen=500)
			self.Ordinate[data] = deque(maxlen=500)
			self.Abs[data] =[]
			self.Ord[data] =[]

			self.plot[data].setData(self.Abs[data],self.Ord[data])