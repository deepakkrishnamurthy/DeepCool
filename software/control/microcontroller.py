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

        # AUTO-DETECT the uController! By Deepak
        ucontroller_ports = [
                p.device
                for p in serial.tools.list_ports.comports()
                if MicrocontrollerDef.DESC in p.description]
        if not ucontroller_ports:
            raise IOError("No {} found".format(MicrocontrollerDef.NAME))
        if len(ucontroller_ports) > 1:
            print('Multiple uControllers found - using the first')
        else:
            print('Using uController found at : {}'.format(ucontroller_ports[0]))

        # establish serial communication
        self.serial = serial.Serial(ucontroller_ports[0],2000000)

        self.hand_shaking_protocol()
        time.sleep(0.2)
        print('Serial Connection Open')

    def hand_shaking_protocol(self):
        # Read string from Arduino
        print('try handshaking')

        print('Pinging uController')

        cmd = bytearray(1)
        cmd[0] = 1
        self.serial.write(cmd)

        rec_number = ord(self.serial.read())

        if(rec_number == 2):
            print('\n ------------Communication established both ways with the uController------------\n')

        print('handshaking finished')

    def close(self):
        self.serial.close()

    def send_temp_setpoint(self, value):        
        # Send this as a 3 byte integer with 1 more byte as a flag
        cmd = bytearray(self.tx_buffer_length)
        cmd[0] = 0 # Set temp set-point
        cmd[1], cmd[2] = byte_operations.split_int_2byte(value)
        self.serial.write(cmd)

    def send_fan_speed(self, value):
        cmd = bytearray(self.tx_buffer_length)
        cmd[0] = 1 # Set fan-speed
        cmd[1], cmd[2] = byte_operations.split_int_2byte(value)
        self.serial.write(cmd)
        print('Sent fan speed {}'.format(value))


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

    

