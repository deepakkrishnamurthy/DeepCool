# set QT_API environment variable
import os 
import sys
import time
from datetime import datetime
os.environ["QT_API"] = "pyqt5"
import qtpy
import pyqtgraph as pg

# qt libraries
from qtpy.QtCore import *
from qtpy.QtWidgets import *
from qtpy.QtGui import *

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True) #enable highdpi scaling
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True) #use highdpi icons

# Definitions
from control._def import *

import control.utils.byte_operations as byte_operations
import control.microcontroller as microcontroller
from control.plotting import PlotWidget
import control.utils.CSV_Tool as CSV_Tool

class MicrocontrollerReceiver(QObject):

	'''
	Receives data from microcontroller and updates the Internal state variables to the latest value
	Connection Map:
	StreamHandler (rec new image) -> getData_microcontroller
	'''
	update_temperature = Signal(float)
	update_plot_1 = Signal(str, float, float)
	update_plot_2 = Signal(str, float, float)

	def __init__(self, microcontroller):
		QObject.__init__(self)

		self.microcontroller = microcontroller
	

		# Define a timer to read the Arduino at regular intervals
		self.timer_read_uController = QTimer()
		self.timer_read_uController.setInterval(MicrocontrollerDef.UCONTROLLER_READ_INTERVAL)
		self.timer_read_uController.timeout.connect(self.getData_microcontroller)
		self.time_start = time.time()
		self.timer_read_uController.start()

		self.stop_signal_received = False

		self.time_now = 0
		self.time_prev = 0

		SAVE_DATA = ['Time', 'Temperature set (C)', 'Temperature measured (C)']

		# Create a new CSV file for data logging
		self.csv_register = CSV_Tool.CSV_Register(header = [SAVE_DATA])

		path, *rest = os.path.split(os.getcwd())
		self.path = os.path.join(path, 'testing_data', 'data' + datetime.now().strftime('%Y-%m-%d %H-%M-%-S')+'.csv')

		self.csv_register.file_directory= self.path
		self.csv_register.start_write()


	def getData_microcontroller(self):

		data = self.microcontroller.read_received_packet_nowait()


		if(data is not None):
			# Parse the data
			

			sensor_voltage_digital = byte_operations.dataNbyte_to_int(data[0:2], 2)
			set_voltage_digital = byte_operations.dataNbyte_to_int(data[2:4], 2)

			# Convert voltage to temperature
			analog_voltage = digital_to_analog(sensor_voltage_digital)
			analog_voltage_set = digital_to_analog(set_voltage_digital)

			temperature_measured = voltage_to_temp(analog_voltage)
			temperature_set = voltage_to_temp(analog_voltage_set)

			print('Temperature measured: {} C'.format(round(temperature_measured, 1)))
			print('Temperature Set: {} C'.format(round(temperature_set,1)))

			self.update_temperature.emit(temperature_measured)

			# Update plots
			time_elapsed = time.time() - self.time_start
			self.update_plot_1.emit('Temperature (measured)', time_elapsed, temperature_measured)
			self.update_plot_2.emit('Temperature (set)', time_elapsed, temperature_set)

			# Log the data to a CSV file
			self.csv_register.write_line([[time_elapsed, temperature_set, temperature_measured]])
			print('wrote data to file')

		else:
			pass


	def stop(self):

		self.stop_signal_received = True
		self.timer_read_uController.stop()
		self.csv_register.close()

		print('Stopped uController receiver')



class TemperatureSettingWidget(QWidget):
	
	temp_setpoint = Signal(float)

	def __init__(self, main=None, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.add_components()

	def add_components(self):

		# Spin box for set temp
		self.entry_temp_setpoint = QDoubleSpinBox()
		self.entry_temp_setpoint.setMinimum(TempControllerDef.TEMP_MIN) 
		self.entry_temp_setpoint.setMaximum(TempControllerDef.TEMP_MAX) 
		self.entry_temp_setpoint.setSingleStep(TempControllerDef.TEMP_STEP_MIN)
		self.entry_temp_setpoint.setValue(TempControllerDef.TEMP_DEFAULT)


		# LCD display for the actual temp
		self.actual_temp_display = pg.ValueLabel(suffix="C")
		self.actual_temp_display.setValue(TempControllerDef.TEMP_DEFAULT)

		# Layout
		layout = QGridLayout()
		layout.addWidget(QLabel('Temperature set-point (C)'), 0,0,1,1)
		layout.addWidget(self.entry_temp_setpoint,1,0,1,1)
		layout.addWidget(QLabel('Temperature measured (C)'), 0,1,1,1)
		layout.addWidget(self.actual_temp_display, 1,1,1,1)

		self.setLayout(layout)

		# Connections
		self.entry_temp_setpoint.valueChanged.connect(self.send_temp_setpoint)



	def send_temp_setpoint(self):
		temp = self.entry_temp_setpoint.value()
		print('Temperature: {}'.format(temp))
		# Convert temp in C to voltage in 12 bit digital
		voltage = temp_to_voltage(temp)

		if(voltage < MicrocontrollerDef.DAC_MIN):
			voltage = MicrocontrollerDef.DAC_MIN
			temp = voltage_to_temp(voltage)
			self.entry_temp_setpoint.setValue(temp)
			print('Out of bounds!')

		elif(voltage > MicrocontrollerDef.DAC_MAX):
			voltage = MicrocontrollerDef.DAC_MAX
			temp = voltage_to_temp(voltage)
			self.entry_temp_setpoint.setValue(temp)
			print('Out of bounds!')

		print('Voltage: {}'.format(voltage))

		voltage_digital = analog_to_digital(voltage)
		print('Voltage digital: {}'.format(voltage_digital))

		self.temp_setpoint.emit(voltage_digital) # Emit the temp set-point in voltage (digital)

	def update_actual_temp_display(self, value):
		self.actual_temp_display.setValue(value)





class DeepCool_GUI(QMainWindow):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		self.setWindowTitle('Deep Cool v0.0.1')

		self.temp_setting_widget = TemperatureSettingWidget()
		self.plot_widget = PlotWidget(title = 'Temperature', data_to_plot = PLOT_VARIABLES)
		self.microcontroller = microcontroller.Microcontroller()
		self.microcontroller_Receiver = MicrocontrollerReceiver(self.microcontroller)
		
		# Layout
		layout = QGridLayout() #layout = QStackedLayout()
		layout.addWidget(self.temp_setting_widget,0,0,1,1)
		layout.addWidget(self.plot_widget,1,0,1,1)

		self.centralWidget = QWidget()
		self.centralWidget.setLayout(layout)
		self.setCentralWidget(self.centralWidget)

		# Connections
		# If temp set-point is changed then send it to the uController.
		self.temp_setting_widget.temp_setpoint.connect(self.microcontroller.send_temp_setpoint)
		# Update the temperature display based on measured value
		self.microcontroller_Receiver.update_temperature.connect(self.temp_setting_widget.update_actual_temp_display)
		# Plot connections
		self.microcontroller_Receiver.update_plot_1.connect(self.plot_widget.update_plot)
		self.microcontroller_Receiver.update_plot_2.connect(self.plot_widget.update_plot)

	def closeEvent(self, event):

		reply = QMessageBox.question(self, 'Message',
			"Are you sure you want to exit?", QMessageBox.Yes | 
			QMessageBox.No, QMessageBox.Yes)

		if reply == QMessageBox.Yes:

			self.microcontroller_Receiver.stop()			

			event.accept()

	
			
		else:
			event.ignore() 
