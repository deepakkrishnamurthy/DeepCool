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
	
	temp_set_point = Signal(float)

	def __init__(self, main=None, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.add_components()

	def add_components(self):

		# Spin box for set temp
		self.entry_temp_setpoint = QDoubleSpinBox()
		self.entry_temp_setpoint.setMinimum(TempControllerDef.TEMP_MIN) 
		self.entry_temp_setpoint.setMaximum(TempControllerDef.TEMP_MIN) 
		self.entry_temp_setpoint.setSingleStep(TempControllerDef.TEMP_STEP_MIN)
		self.entry_temp_setpoint.setValue(TempControllerDef.TEMP_DEFAULT)


		# LCD display for the actual temp
		self.actual_temp_display = QLCDNumber()
		self.actual_temp_display.setNumDigits(3)
		self.actual_temp_display.display(empControllerDef.TEMP_DEFAULT)

		# Layout
		layout = QGridLayout()
		layout.addWidget(self.entry_temp_setpoint,0,0,1,1)
		layout.addWidget(self.actual_temp_display, 0,1,1,1)

		self.setLayout(layout)

		# Connections
		self.entry_temp_setpoint.valueChanged.connect(self.send_temp_setpoint)



	def send_temp_setpoint(self):
		self.temp_set_point.emit(self.entry_temp_setpoint.Value())
		print('Sent temperature set-point: {}'.format(self.entry_temp_setpoint.Value()))

	def update_actual_temp_display(self, value):
		self.actual_temp_display.display(value)




class DeepCool_GUI(QMainWindow):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		self.setWindowTitle('Deep Cool v0.0.1')

		self.temp_setting_widget = TemperatureSettingWidget()
		self.microcontroller = microcontroller.MicroController()

		# Layout
		layout = QGridLayout() #layout = QStackedLayout()

		layout.addWidget(self.temp_setting_widget)

		self.centralWidget = QWidget()
		self.centralWidget.setLayout(layout)
		self.setCentralWidget(self.centralWidget)


		# Connections
		# If temp set-point is changed then send it to the uController.