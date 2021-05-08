import platform
import serial
import serial.tools.list_ports
import time
import numpy as np

from control._def import *
import control.utils.byte_operations as byte_operations

# add user to the dialout group to avoid the need to use sudo

class Microcontroller():
    def __init__(self,parent=None):
        self.serial = None
        self.platform_name = platform.system()
        self.tx_buffer_length = MicrocontrollerDef.CMD_LENGTH
        self.rx_buffer_length = MicrocontrollerDef.MSG_LENGTH

        # AUTO-DETECT the Arduino! By Deepak
        arduino_ports = [
                p.device
                for p in serial.tools.list_ports.comports()
                if 'Arduino' in p.description]
        if not arduino_ports:
            raise IOError("No Arduino found")
        if len(arduino_ports) > 1:
            print('Multiple Arduinos found - using the first')
        else:
            print('Using Arduino found at : {}'.format(arduino_ports[0]))

        # establish serial communication
        self.serial = serial.Serial(arduino_ports[0],2000000)
        time.sleep(0.2)
        print('Serial Connection Open')

    def close(self):
        self.serial.close()

    def send_temp_setpoint(self, value):
        # Send this as a 3 byte integer with 1 more byte as a flag
        cmd = bytearray(self.tx_buffer_length)
        cmd[0] = 0 # Set temp set-point
        cmd[1], cmd[2] = byte_operations.split_int_2byte(value)
        self.serial.write(cmd)

    def toggle_temp_control(self):
        pass

    def read_received_packet(self):
        # wait to receive data
        while self.serial.in_waiting==0:
            pass
        while self.serial.in_waiting % self.rx_buffer_length != 0:
            pass
        num_bytes_in_rx_buffer = self.serial.in_waiting

        # get rid of old data
        if num_bytes_in_rx_buffer > self.rx_buffer_length:
            # print('getting rid of old data')
            for i in range(num_bytes_in_rx_buffer-self.rx_buffer_length):
                self.serial.read()
        # read the buffer
        data=[]
        for i in range(self.rx_buffer_length):
            data.append(ord(self.serial.read()))
        return data

    def read_received_packet_nowait(self):
        # wait to receive data
        if self.serial.in_waiting==0:
            return None
        if self.serial.in_waiting % self.rx_buffer_length != 0:
            return None
        # get rid of old data
        num_bytes_in_rx_buffer = self.serial.in_waiting
        if num_bytes_in_rx_buffer > self.rx_buffer_length:
            # print('getting rid of old data')
            for i in range(num_bytes_in_rx_buffer-self.rx_buffer_length):
                self.serial.read()
        
        # read the buffer
        data=[]
        for i in range(self.rx_buffer_length):
            data.append(ord(self.serial.read()))
        return data

    def temp_to_voltage(self, temp):
        ''' Convert the temp value to a voltage
        '''
        voltage = TempControllerDef.SENSOR_CURRENT*TempControllerDef.THERMISTOR_LUT(temp)
        return voltage

    def analog_to_digital(self, analog):
        ''' Convert analog voltage between 0 to Vdd of uController to a digital-value based on uController ADC
        '''
        digital = int((analog/3.3)*MicrocontrollerDef.DAC_RES) # Int betwee 0 and 2^DAC_RES

        return digital 

