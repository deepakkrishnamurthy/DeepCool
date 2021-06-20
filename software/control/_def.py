import os
import pandas as pd
from scipy import interpolate

class MicrocontrollerDef:
	 # Time interval for reading micro Controller (ms)
	UCONTROLLER_READ_INTERVAL = 100 
	MSG_LENGTH = 4
	CMD_LENGTH = 3
	
	DAC_RES = 12 # Arduino Due DAC resolution (set to 12 bits)
	ADC_RES = 12 # Arduino Due ADC resolution (set to 12 bits)
	VDD = 3.3 # uController voltage
	DAC_MIN = 0.516 # Min of DAC voltage (Arduino Due) 
	DAC_MAX = 2.72  # Max of DAC voltage (Arduino Due)

	N_SENSORS = 4 # No:of temp sensors in addition to the one connected to the PTC temp controller.
	FIXED_RESISTANCE = 10000 # Fixed resistance in the voltage divider. 
	MSG_LENGTH += N_SENSORS*2
	def __init__(self):
		pass

class TempControllerDef:

	SENSOR_CURRENT = 100e-6 # Sensor current in Amps
	path, *rest = os.path.split(os.getcwd())
	print(path)
	thermistor_data_path = os.path.join(path, 'thermistor_data/10k_littlefuse.csv')
	thermistor_data = pd.read_csv(thermistor_data_path)

	print('Max resistance: {} Ohms'.format(max(thermistor_data['Resistance (Ohms)'])))
	print('Min resistance: {} Ohms'.format(min(thermistor_data['Resistance (Ohms)'])))

	THERMISTOR_LUT_TEMP_TO_RES = interpolate.interp1d(thermistor_data['Temp (C)'], thermistor_data['Resistance (Ohms)'],) # Converts temp in C to Resistance in Ohms
	THERMISTOR_LUT_RES_TO_TEMP = interpolate.interp1d(thermistor_data['Resistance (Ohms)'], thermistor_data['Temp (C)']) # Converts Resistance in Ohms to temp in C

	TEMP_MIN = 4
	TEMP_MAX = 40
	TEMP_STEP_MIN = 0.1
	TEMP_DEFAULT = 20.0


	def __init__(self):
		pass

def temp_to_voltage(temp):
	''' Convert the temp value to a voltage
	'''
	voltage = TempControllerDef.SENSOR_CURRENT*TempControllerDef.THERMISTOR_LUT_TEMP_TO_RES(temp)
	return voltage

def voltage_to_temp(voltage):
	''' Convert the temp value to a voltage
	'''
	resistance = voltage/TempControllerDef.SENSOR_CURRENT
	temp = float(TempControllerDef.THERMISTOR_LUT_RES_TO_TEMP(resistance))
	return temp


def analog_to_digital(analog):
	''' Convert analog voltage to a digital-value based on uController DAC's voltage limits and resolution
	'''
	digital = int(((analog - MicrocontrollerDef.DAC_MIN)/(MicrocontrollerDef.DAC_MAX - MicrocontrollerDef.DAC_MIN))*(2**MicrocontrollerDef.DAC_RES)) # Int between 0 and 2^DAC_RES

	return digital 

def digital_to_analog(digital):
	# Convert digital value measured by uController ADC into Analog voltage
	analog = float((digital/(2**MicrocontrollerDef.ADC_RES))*MicrocontrollerDef.VDD) # Int betwee 0 and 2^DAC_RES

	return analog

def sensor_reading_to_temp(value):
	# Sensor reading is digital value between 0 and 2^ADC_RES
	measured_resistance = MicrocontrollerDef.FIXED_RESISTANCE/(2**MicrocontrollerDef.ADC_RES/float(value) - 1)

	measured_temp = TempControllerDef.THERMISTOR_LUT_RES_TO_TEMP(measured_resistance)

	return measured_temp


PLOT_VARIABLES = ['Temperature (measured)', 'Temperature (set)']

PLOT_COLORS = {'Temperature (measured)':'r','Temperature (set)':'c'}

PLOT_UNITS = {'Temperature (measured)':'C','Temperature (set)':'C'}





