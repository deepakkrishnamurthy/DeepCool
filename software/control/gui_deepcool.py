# set QT_API environment variable
import os 
import sys
os.environ["QT_API"] = "pyqt5"
import qtpy

# qt libraries
from qtpy.QtCore import *
from qtpy.QtWidgets import *
from qtpy.QtGui import *

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True) #enable highdpi scaling
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True) #use highdpi icons

# Definitions
from control._def import *

import control.microcontroller as microcontroller

class TemperatureSettingWidget(QWidget):
	def __init__(self, main=None, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.add_components()

	def add_components(self):

		# Spin box for set temp
		self.entry_temp_setpoint = QDoubleSpinBox()
		self.entry_temp_setpoint.setMinimum(TempControllerDef.TEMP_MIN) 
		self.entry_temp_setpoint.setMaximum(TempControllerDef.TEMP_MIN) 
		self.entry_temp_setpointe.setSingleStep(TempControllerDef.TEMP_STEP_MIN)
		self.entry_temp_setpoint.setValue(TempControllerDef.TEMP_DEFAULT)


		# LCD display for the actual temp
		self.actual_temp_display = QLCDNumber()
		self.actual_temp_display.setNumDigits(3)
		self.actual_temp_display.display(empControllerDef.TEMP_DEFAULT)


	def send_temp_setpoint(self):
		pass

	def update_actual_temp_display(self, value):
		pass




class DeepCool_GUI(QMainWindow):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		self.setWindowTitle('Deep Cool v0.0.1')


		# Layout
		layout = QGridLayout() #layout = QStackedLayout()


		self.centralWidget = QWidget()
		self.centralWidget.setLayout(layout)
		self.setCentralWidget(self.centralWidget)