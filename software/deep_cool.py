# set QT_API environment variable
import os 
import sys
os.environ["QT_API"] = "pyqt5"
import qtpy

# qt libraries
from qtpy.QtCore import *
from qtpy.QtWidgets import *
from qtpy.QtGui import *




# app specific libraries
#import control.gui as gui
#import control.gui_2cameras_async as gui
import control.gui_deepcool as gui

if __name__ == "__main__":

	app = QApplication([])
	
	# Main GUI window
	win = gui.DeepCool_GUI()

	win.show()

	app.exec_() #

	sys.exit()

