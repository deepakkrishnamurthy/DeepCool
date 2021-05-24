# set QT_API environment variable
import os 
import sys
import time
from datetime import datetime
os.environ["QT_API"] = "pyqt5"
import qtpy
import pyqtgraph as pg
import numpy as np

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
	sensor_readings_signal = Signal(np.ndarray)

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
		self.save_data = False

		self.time_now = 0
		self.time_prev = 0

		self.sensor_readings = np.zeros(MicrocontrollerDef.N_SENSORS)
		self.sensor_readings_temp = np.zeros(MicrocontrollerDef.N_SENSORS)

		self.SAVE_DATA = ['Time', 'Temperature set (C)', 'Temperature measured (C)'] + ['Sensor {} (C)'.format(ii+1) for ii in range(MicrocontrollerDef.N_SENSORS)]
		self.csv_register = None

		


	def getData_microcontroller(self):

		data = self.microcontroller.read_received_packet_nowait()


		if(data is not None):
			# Parse the data
			

			sensor_voltage_digital = byte_operations.dataNbyte_to_int(data[0:2], 2)
			set_voltage_digital = byte_operations.dataNbyte_to_int(data[2:4], 2)

			# Read data from remaining sensors (if connected)
			for ii in range(MicrocontrollerDef.N_SENSORS):
				# The sensor readings will be a voltage from the resistive divider so the conversion formula is different
				self.sensor_readings[ii] = byte_operations.dataNbyte_to_int(data[4 + 2*ii:4 + 2*(ii+1)], 2)
				print(self.sensor_readings[ii])

			# Convert voltage to temperature
			analog_voltage = digital_to_analog(sensor_voltage_digital)
			analog_voltage_set = digital_to_analog(set_voltage_digital)

			temperature_measured = voltage_to_temp(analog_voltage)
			temperature_set = voltage_to_temp(analog_voltage_set)

			print('Temperature measured: {} C'.format(round(temperature_measured, 1)))
			print('Temperature Set: {} C'.format(round(temperature_set,1)))

			# @@@ Convert the sensor readings (not connected to Temp controller) to a temperature.
			for ii in range(MicrocontrollerDef.N_SENSORS):
				self.sensor_readings_temp[ii] = sensor_reading_to_temp(self.sensor_readings[ii])


			self.update_temperature.emit(temperature_measured)

			# Update plots
			time_elapsed = time.time() - self.time_start
			self.update_plot_1.emit('Temperature (measured)', time_elapsed, temperature_measured)
			self.update_plot_2.emit('Temperature (set)', time_elapsed, temperature_set)

			if(MicrocontrollerDef.N_SENSORS>0):
				self.sensor_readings_signal.emit(self.sensor_readings_temp)
			# Log the data to a CSV file
			if(self.save_data):
				self.csv_register.write_line([[time_elapsed, temperature_set, temperature_measured] + [self.sensor_readings_temp[ii] for ii in range(MicrocontrollerDef.N_SENSORS)]])
				print('wrote data to file')

		else:
			pass

	def toggle_save_data(self, flag):
		save_data_prev = self.save_data
		self.save_data = flag

		if(save_data_prev == False and self.save_data == True):

			# Create a new CSV file for data logging
			self.csv_register = CSV_Tool.CSV_Register(header = [self.SAVE_DATA])

			path, *rest = os.path.split(os.getcwd())
			self.path = os.path.join(path, 'testing_data', 'data' + datetime.now().strftime('%Y-%m-%d %H-%M-%-S')+'.csv')

			self.csv_register.file_directory= self.path
			self.csv_register.start_write()

		elif (save_data_prev == True and self.save_data == False):
			self.csv_register.close()
			self.csv_register = None


	def stop(self):

		self.stop_signal_received = True
		self.timer_read_uController.stop()
		if(self.csv_register):
			self.csv_register.close()

		print('Stopped uController receiver')



class TemperatureControlWidget(QWidget):
	
	temp_setpoint = Signal(float)
	fan_speed = Signal(int)
	save_data_signal = Signal(bool)

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


		# Display for the actual temp (from Temp controller)
		self.actual_temp_display = pg.ValueLabel(suffix="C")
		self.actual_temp_display.setValue(TempControllerDef.TEMP_DEFAULT)

		self.temp_display = {}
		# Display for actual temp from other temperature sensors
		for ii in range(MicrocontrollerDef.N_SENSORS):
			self.temp_display[ii] = pg.ValueLabel(suffix="C")

		# Button for toggling data saving
		self.save_data_button = QPushButton('Save data')
		self.save_data_button.setCheckable(True)
		self.save_data_button.setChecked(False)

		# Slide for setting the fan-speed
		self.slider_speed = QSlider(Qt.Vertical)
		self.slider_speed.setTickPosition(QSlider.TicksBelow)
		self.slider_speed.setMinimum(0)
		self.slider_speed.setMaximum(100)
		self.slider_speed.setValue(50)
		self.slider_speed.setSingleStep(1)

		# Layout
		layout = QGridLayout()
		layout.addWidget(QLabel('Temperature set-point (C)'), 0,0,1,1)
		layout.addWidget(self.entry_temp_setpoint,1,0,1,1)
		layout.addWidget(QLabel('Temperature measured (C)'), 0,1,1,1)
		layout.addWidget(self.actual_temp_display, 1,1,1,1)

		for ii in range(MicrocontrollerDef.N_SENSORS):
			layout.addWidget(QLabel('Sensor {} (C)'.format(ii+1)), 2+ii,0)
			layout.addWidget(self.temp_display[ii], 2+ii, 1)

		layout.addWidget(QLabel('Fan speed (%)'),0,2,1,1)
		layout.addWidget(self.slider_speed,1,2,2+MicrocontrollerDef.N_SENSORS-1,1)

		layout.addWidget(self.save_data_button,0,3)

		self.setLayout(layout)

		# Connections
		self.entry_temp_setpoint.valueChanged.connect(self.send_temp_setpoint)
		self.save_data_button.clicked.connect(self.handle_save_button)
		self.slider_speed.valueChanged.connect(self.send_fan_speed)


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

	def send_fan_speed(self):
		value = self.slider_speed.value()

		digital_value = int((value/100)*(2**MicrocontrollerDef.DAC_RES))

		self.fan_speed.emit(digital_value)

	def update_actual_temp_display(self, value):
		self.actual_temp_display.setValue(value)

	def update_sensor_temp_display(self, value):
		# Update sensor readings from other sensors (not connected to Temp controller)
		for ii in range(MicrocontrollerDef.N_SENSORS):

			self.temp_display[ii].setValue(value[ii])			

	def handle_save_button(self):

		if(self.save_data_button.isChecked()):
			self.save_data_signal.emit(True)
		else:
			self.save_data_signal.emit(False)





class DeepCool_GUI(QMainWindow):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		self.setWindowTitle('Deep Cool v0.0.1')

		self.temp_setting_widget = TemperatureControlWidget()
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
		self.temp_setting_widget.save_data_signal.connect(self.microcontroller_Receiver.toggle_save_data)
		self.temp_setting_widget.fan_speed.connect(self.microcontroller.send_fan_speed)
		# Update the temperature display based on measured value
		self.microcontroller_Receiver.update_temperature.connect(self.temp_setting_widget.update_actual_temp_display)
		self.microcontroller_Receiver.sensor_readings_signal.connect(self.temp_setting_widget.update_sensor_temp_display)
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
