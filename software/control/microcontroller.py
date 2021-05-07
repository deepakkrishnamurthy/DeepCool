import platform
import serial
import serial.tools.list_ports
import time
import numpy as np

from control._def import *

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

    def send_temp_setpoint(self):
        pass

    def toggle_temp_control(self):
        pass


    def toggle_LED(self,state):
        cmd = bytearray(self.tx_buffer_length)
        cmd[0] = 3
        cmd[1] = state
        self.serial.write(cmd)
    
    def toggle_laser(self,state):
        cmd = bytearray(self.tx_buffer_length)
        cmd[0] = 4
        cmd[1] = state
        self.serial.write(cmd)

    

    def move_theta_nonblocking(self,delta):
        direction = int((np.sign(delta)+1)/2)
        n_microsteps = abs(delta*Motion.MAX_MICROSTEPS)
        if n_microsteps > 65535:
            n_microsteps = 65535
        cmd = bytearray(self.tx_buffer_length)
        cmd[0] = 3
        cmd[1] = 1-direction
        cmd[2] = int(n_microsteps) >> 8
        cmd[3] = int(n_microsteps) & 0xff
        self.serial.write(cmd)
        # print('Theta non-blocking command sent to uController: {}'.format(n_microsteps))


    # Convert below functions to be compatible with squid/octopi serial interface.
    def send_tracking_command(self, tracking_flag):
        cmd = bytearray(self.tx_buffer_length)
        cmd[0] = 4
        cmd[1] = tracking_flag

        self.serial.write(cmd)


    def send_liquid_lens_amp(self, amp):
        cmd = bytearray(self.tx_buffer_length)
        cmd[0] = 8
        cmd[1] = 1
        cmd[2], cmd[3] = split_int_2byte(round(amp*100)) 

        self.serial.write(cmd)

    def send_command(self,command):
        cmd = bytearray(self.tx_buffer_length)
        self.serial.write(cmd)

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