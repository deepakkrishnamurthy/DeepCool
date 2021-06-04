// Set a temperature and measure the sensor reading from a temperature controller.
// - Temperature value is set by sending an analog value via a DAC
// - Sensor value is detected using the Arduino's built-in ADC
// - The firmware outputs the sensor reading as a voltage. 
// - Conversion of this voltage to an actual temperature value is handled by the software. 

#include <Wire.h>

//#define TESTING
#define temperature_sensor_1 A0 
#define set_point_input A1
#define fan_speed_input A2
#define fan_speed_pin 7
#define motor_pin_1 8
#define motor_pin_2 9

//# define SENSORS
static const int N_SENSORS = 0; // No: of additional temp sensors

#ifdef SENSORS
  static const int sensor_pin[N_SENSORS] = {A3, A4};
  int sensor_reading[N_SENSORS] = {0}; 
#else
  static const int sensor_pin[1] = {A3};
  int sensor_reading[1] = {0};
#endif
 
/***************************************************************************************************/
/***************************************** Communications ******************************************/
/***************************************************************************************************/
static const int CMD_LENGTH = 3;
static const int MSG_LENGTH = 4 + 2*N_SENSORS;
byte buffer_rx[500];
byte buffer_tx[MSG_LENGTH];
volatile int buffer_rx_ptr;
bool calculateCRC_tx = true;
volatile bool isReceived = false;

const int dac_resolution = 4095; // 12-bit DAC resolution
const int adc_resolution = 4095; // 10-bit ADC resolution (Arduino)

const int update_time = 100; // Update time in ms
const int send_data_time = 1000; // Rate at which data is sent to computer
int set_voltage_digital = 0; // or in the digital sense: 0-4095
int set_voltage_input_digital = 1861, set_voltage_input_digital_prev = 0 ;
int sensor_voltage_controller, set_voltage_actual;



int fan_speed = 0; // Analog input for fab speed

unsigned long last_sensor_read=0, last_send_time=0;

void setup() 
{
  SerialUSB.begin (20000000);
  while(!SerialUSB); //Wait until connection is established
  
  analogWriteResolution(12);
  analogReadResolution(12);

  pinMode(fan_speed_pin, OUTPUT);
  pinMode(motor_pin_1, OUTPUT);
  pinMode(motor_pin_2, OUTPUT);

  digitalWrite(motor_pin_1, HIGH);
  digitalWrite(motor_pin_2, LOW);

  

}

void loop() 
{
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
           set_voltage_input_digital = long(buffer_rx[1])*256 + long(buffer_rx[2]);
          
        }
        else if(buffer_rx[0]==1)
        {
          // New set-point temp received.
           fan_speed = long(buffer_rx[1])*256 + long(buffer_rx[2]);

           // Send PWM signal to the motor-driver
          analogWrite(fan_speed_pin, fan_speed);
          
        }
    }
  }
  
  // If the set-point is changed then write the new value to the DAC
  if(set_voltage_input_digital != set_voltage_input_digital_prev)
  {    
    analogWrite(DAC1, set_voltage_input_digital);
    set_voltage_input_digital_prev = set_voltage_input_digital;  

   
  }
  // Read the sensor
  if(millis() - last_sensor_read >= update_time)
  {
    last_sensor_read = millis();

    // Read the sensor
    #ifdef TESTING
    // Testing
      sensor_voltage_controller = 310;
      set_voltage_actual = int(adc_resolution*(0.516 + set_voltage_input_digital*(2.72-0.516)/float(dac_resolution))/3.3); 
      for (int i=0;i<N_SENSORS;i++)
      {
        sensor_reading[i] = 2048;
      }
    #else 
        sensor_voltage_controller = analogRead(temperature_sensor_1);
        set_voltage_actual = analogRead(set_point_input);

        // Read the additional temp sensors
        for (int i=0;i<N_SENSORS;i++)
        {
            sensor_reading[i] = analogRead(sensor_pin[i]);
        }
        // Read the fan-speed setting
//        fan_speed = analogRead(fan_speed_input);
    #endif
     
    
  }

//
//  // Send the temperature to the computer
//  // @@@ ADD SEND CODE HERE @@@
  if(millis() - last_send_time >= send_data_time)
  {
      last_send_time = millis();
      // send the measured temperature value
      buffer_tx[0] = byte(sensor_voltage_controller>>8);
      buffer_tx[1] = byte(sensor_voltage_controller%256);

      // send the set-temperature value (actual)
      buffer_tx[2] = byte(set_voltage_actual>>8);
      buffer_tx[3] = byte(set_voltage_actual%256);

      for (int i=0;i<N_SENSORS;i++)
      {
        buffer_tx[4+2*i] = byte(sensor_reading[i]>>8);
        buffer_tx[4+2*i+1] = byte(sensor_reading[i]%256);        
      }

      SerialUSB.write(buffer_tx, MSG_LENGTH);
    
  }

//   # ifdef TESTING
//      SerialUSB.println(set_voltage_digital);
//      SerialUSB.println('Sensor voltage');
//      SerialUSB.println(sensor_voltage_controller);
//    #endif

    

}
