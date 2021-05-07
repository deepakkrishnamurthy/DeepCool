import os
import pandas as pd
from scipy import interpolate

class MicrocontrollerDef:
     # Time interval for reading micro Controller (ms)
    UCONTROLLER_READ_INTERVAL = 25 
    MSG_LENGTH = 12
    CMD_LENGTH = 4
    N_BYTES_POS = 3
    RUN_OPENLOOP = False # Determines whether stepper/encoders are used to calculate stage positions.

    def __init__(self):
        pass

class TempControllerDef:

	SENSOR_CURRENT = 100e-6 # Sensor current in Amps
	thermistor_data_path = os.path.join(os.getcwd, 'thermistor_data', '10k_littlefuse.csv')
	thermistor_data = pd.read_csv(thermistor_data_path)

	THERMISTOR_LUT = interpolate.interp1d(thermistor_data['Temp (C)'], thermistor_data['Resistance (Ohms)'],) # Converts temp to Resistance in Ohms

	TEMP_MIN = 4
	TEMP_MAX = 50
	TEMP_STEP_MIN = 0.1
	TEMP_DEFAULT = 20.0
	def __init__(self):
        pass




