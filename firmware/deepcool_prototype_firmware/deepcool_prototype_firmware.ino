// Set a temperature and measure the sensor reading from a temperature controller.
// - Temperature value is set by sending an analog value via a DAC
// - Sensor value is detected using the Arduino's built-in ADC
// - The firmware outputs the sensor reading as a voltage. 
// - Conversion of this voltage to an actual temperature value is handled by the software. 

#include <Wire.h>

# define TESTING

# define N_SENSORS 1
#define temperature_sensor_1 A0 
#define set_point_input A1

const int dac_resolution = 4095; // 12-bit DAC resolution
const int adc_resolution = 1023; // 1--bit ADC resolution (Arduino)

const int update_time = 1000; // Update time in ms
const int send_data_time = 1000; // Rate at which data is sent to computer
int set_voltage_digital = 0; // or in the digital sense: 0-4095
int set_voltage_input_digital = 0, set_voltage_input_digital_prev = 0 ;
float set_voltage_input_analog = 0, set_voltage_input_analog_prev=0.0;
int sensor_voltage;

unsigned long last_sensor_read=0, last_send_time=0;

void setup() 
{
  SerialUSB.begin(9600);
  SerialUSB.println("Hello!");
  
  analogWriteResolution(12);

  
  
}

void loop() {


  // Receive the new set-temperature from the computer if available
  // @@@ ADD REC CODE HERE @@@
  //Data reception: the data is read at the frequency of the computer
  while (SerialUSB.available()) 
  { 
    buffer_rx[buffer_rx_ptr] = SerialUSB.read();
    buffer_rx_ptr = buffer_rx_ptr + 1;
    if (buffer_rx_ptr == CMD_LENGTH) 
    {
        buffer_rx_ptr = 0;
 
        isReceived=true;

        if(buffer_rx[0]==0)
        {
          // New set-point temp received.
           set_voltage_input_digital = long(buffer_rx[1])*256 + long(buffer_rx[2])
          
        }

  #ifdef TESTING
    // For testing use a potentiometer.
    set_voltage_input_digital = analogRead(set_point_input); // Set point voltage red by the ADC
    set_voltage_input_analog = (set_voltage_input_digital/float(adc_resolution))*3.3; // Set-point voltage in volts  
  # endif
  
  // If the set-point is changed then write the new value to the DAC
  if(set_voltage_input_digital != set_voltage_input_digital_prev)
  {    
    analogWrite(DAC1, set_voltage_input_digital);
    set_voltage_input_digital_prev = set_voltage_input_digital;  

   
  }
//
  if(millis() - last_sensor_read >= update_time)
  {
    last_sensor_read = millis();

    // Read the sensor
    sensor_voltage = analogRead(temperature_sensor_1);
    // Map the reading to the same resolution as the DAC
    sensor_voltage = map(sensor_voltage, 0, adc_resolution, 0, dac_resolution);
  
   

  }

  

  
//
//  // Send the temperature to the computer
//  // @@@ ADD SEND CODE HERE @@@
  if(millis() - last_send_time >= send_data_time)
  {
      
      // send the actual temperature value
      buffer_tx[0] = byte(sensor_voltage>>8);
      buffer_tx[1] = byte(sensor_voltage%256);

      // send the set-temperature value
      buffer_tx[0] = byte(set_voltage_input_digital>>8);
      buffer_tx[1] = byte(set_voltage_input_digital%256);
    
  }

   # ifdef TESTING
      SerialUSB.println(set_voltage_input_analog);
      SerialUSB.println(set_voltage_digital);
      SerialUSB.println('Sensor voltage');
      SerialUSB.println(sensor_voltage);
    #endif

    

}
