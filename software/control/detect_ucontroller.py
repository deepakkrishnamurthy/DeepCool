import platform
import serial
import serial.tools.list_ports
 # AUTO-DETECT microcontroller! By Deepak



for p in serial.tools.list_ports.comports():
    print(p.description)

# arduino_ports = [
#         p.device
#         for p in serial.tools.list_ports.comports()
#         if 'Arduino' in p.description]
# if not arduino_ports:
#     raise IOError("No Arduino found")
# if len(arduino_ports) > 1:
#     print('Multiple Arduinos found - using the first')
# else:
#     print('Using Arduino found at : {}'.format(arduino_ports[0]))

# # establish serial communication
# self.serial = serial.Serial(arduino_ports[0],2000000)
# time.sleep(0.2)
# print('Serial Connection Open')