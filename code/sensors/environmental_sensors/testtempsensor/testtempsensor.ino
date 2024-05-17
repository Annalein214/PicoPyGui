// test only one temperature sensor
// send value 2 via serial after bootup



// need this library for the proprietary communication with dallas sensors
#include <OneWire.h>
// make commands easier with this library
#include <DallasTemperature.h>

// Data wire bus
#define ONE_WIRE_BUS 2

// Setup a oneWire instance to communicate with any OneWire devices
OneWire oneWire(ONE_WIRE_BUS);
// Pass our oneWire reference to Dallas Temperature sensor 
DallasTemperature sensors(&oneWire);

DeviceAddress tempDeviceAddress; // We'll use this variable to store a found device address

// ------------------------------------------------------------

// function to print a device address
void printAddress(DeviceAddress deviceAddress) {
  for (uint8_t i = 0; i < 8; i++) {
    if (deviceAddress[i] < 16) Serial.print("0");
      Serial.print(deviceAddress[i], HEX);
  }
}

void sendTempValue(){
  /*// Call sensors.requestTemperatures() to issue a global temperature and Requests to all devices on the bus
  sensors.requestTemperatures(); 
  
  Serial.print("Temperature ");
  // Why "byIndex"? You can have more than one IC on the same bus. 0 refers to the first IC on the wire
  Serial.println(sensors.getTempCByIndex(0));
  */
  float tempC = sensors.getTempC(tempDeviceAddress);
  Serial.print("Temperature: ");
  if (tempC == DEVICE_DISCONNECTED_C)
  {
    Serial.print(-100);
    return;
  }
  Serial.print(tempC);
  Serial.println(" °C");
}

// ------------------------------------------------------------

void setup(){
  Serial.begin(9600);
  

  // search for boards
  // Start up the library
  sensors.begin();
  Serial.print("Found ");
  Serial.print(sensors.getDeviceCount(), DEC);
  Serial.println(" devices.");

  if(sensors.getAddress(tempDeviceAddress, 0)) {
      Serial.print("Found device ");
      Serial.print(0, DEC);
      Serial.print(" with address: ");
      printAddress(tempDeviceAddress);
      Serial.println();
		} else {
		  Serial.print("Found ghost device at ");
		  Serial.print(0, DEC);
		  Serial.print(" but could not detect address. Check power and cabling");
		}

    // report parasite power requirements
  // should be OFF
  Serial.print("Parasite power is: ");
  if (sensors.isParasitePowerMode()) Serial.println("ON");
  else Serial.println("OFF");

    // highest resolution is 12, should give 12
    //sensors.setResolution(tempDeviceAddress, 12);
    Serial.print("Device 0 Resolution: ");
    Serial.print(sensors.getResolution(tempDeviceAddress), DEC);
    Serial.println();
}


// ------------------------------------------------------------

void loop(){
  // check if new messages are incoming
  if (1 && Serial.available() > 0){
      //digitalWrite(LED_BUILTIN, HIGH);
      int val = char(Serial.read()) - '0';
      if (val == 2){
        sendTempValue();
      }
      //delay(200);
  }
}