import os
import pandas as pd
from scipy import interpolate

class MicrocontrollerDef:
	 # Time interval for reading micro Controller (ms)
	UCONTROLLER_READ_INTERVAL = 100 
	MSG_LENGTH = 4
	CMD_LENGTH = 3
	
	DAC_RES = 12 
	ADC_RES = 12
	VDD = 3.3 # uController voltage
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
	TEMP_MAX = 50
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
	print('Resistance :{} Ohms'.format(resistance))
	temp = float(TempControllerDef.THERMISTOR_LUT_RES_TO_TEMP(resistance))
	return temp


def analog_to_digital(analog):
	''' Convert analog voltage between 0 to Vdd of uController to a digital-value based on uController ADC
	'''
	digital = int((analog/MicrocontrollerDef.VDD)*(2**MicrocontrollerDef.DAC_RES)) # Int betwee 0 and 2^DAC_RES

	return digital 

def digital_to_analog(digital):

	analog = float((digital/(2**MicrocontrollerDef.DAC_RES))*MicrocontrollerDef.VDD) # Int betwee 0 and 2^DAC_RES

	return analog





