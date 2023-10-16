/*
 * Rui Santos
 * Complete Project Details https://randomnerdtutorials.com



 --- Standard output: ---
 --- Setup ---
Locating devices...Found 1 devices.
Found device 0 with addreLocating devices...Found 1 devices.
Found device 0 with address: 283023E70D00009A
  --- send "1" per serial and you get:
Device: 0, Temperature: 25.87;Device: 0, Temperature: 25.87;


*/

#include <OneWire.h>
#include <DallasTemperature.h>

// Data wire is plugged into port 4 on the Arduino
#define ONE_WIRE_BUS 2
// Setup a oneWire instance to communicate with any OneWire devices (not just Maxim/Dallas temperature ICs)
OneWire oneWire(ONE_WIRE_BUS);

// Pass our oneWire reference to Dallas Temperature. 
DallasTemperature sensors(&oneWire);

int numberOfDevices; // Number of temperature devices found

DeviceAddress tempDeviceAddress; // We'll use this variable to store a found device address

void setup(void) {
  // start serial port
  Serial.begin(9600);
  
  // Start up the library
  sensors.begin();
  
  // Grab a count of devices on the wire
  numberOfDevices = sensors.getDeviceCount();
  
  // locate devices on the bus
  Serial.print("Locating devices...");
  Serial.print("Found ");
  Serial.print(numberOfDevices, DEC);
  Serial.println(" devices.");

  // Loop through each device, print out address
  for(int i=0;i<numberOfDevices; i++) {
    // Search the wire for address
    if(sensors.getAddress(tempDeviceAddress, i)) {
      Serial.print("Found device ");
      Serial.print(i, DEC);
      Serial.print(" with address: ");
      printAddress(tempDeviceAddress);
      Serial.println();
		} else {
		  Serial.print("Found ghost device at ");
		  Serial.print(i, DEC);
		  Serial.print(" but could not detect address. Check power and cabling");
		}
  }
}

void sendValue(){
  sensors.requestTemperatures(); // Send the command to get temperatures
  
  // Loop through each device, print out temperature data
  for(int i=0;i<numberOfDevices; i++) {
    // Search the wire for address
    if(sensors.getAddress(tempDeviceAddress, i)){
		
		// Output the device ID
		Serial.print("Device: ");
		Serial.print(i,DEC);
    

    // Print the data
    float tempC = sensors.getTempC(tempDeviceAddress);
    Serial.print(", Temperature: ");
    Serial.print(tempC);
    Serial.print("; ");
    } 	
  }
  Serial.println();
}

// function to print a device address
void printAddress(DeviceAddress deviceAddress) {
  for (uint8_t i = 0; i < 8; i++) {
    if (deviceAddress[i] < 16) Serial.print("0");
      Serial.print(deviceAddress[i], HEX);
  }
}

void loop(void) { 
  // check if new messages are incoming
  if (Serial.available() > 0){
      int val = char(Serial.read()) - '0';
      if (val == 1){
        sendValue();
      }
      delay(200);
  }
}