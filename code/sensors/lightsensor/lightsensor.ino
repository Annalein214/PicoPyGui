#include <OneWire.h>
#include <DallasTemperature.h>

// Data wire is conntec to the Arduino digital pin 4
#define ONE_WIRE_BUS 3

int LDR = A0; // Analoger Pin als LDR Eingang
int sensorValue = 0; // Variable für den Sensorwert mit 0 als Startwert
int val=0; // for serial communication

// Setup a oneWire instance to communicate with any OneWire devices
OneWire oneWire(ONE_WIRE_BUS);
// Pass our oneWire reference to Dallas Temperature sensor 
DallasTemperature sensors(&oneWire);


void setup(){
  Serial.begin(9600);
  // Start up the library
  sensors.begin();
}

void sendDiodeValue(){
  sensorValue =analogRead(LDR); //
  float voltage = sensorValue * (5000.0 / 1023.0);
  Serial.print("Diode ");
  Serial.println(voltage); //Ausgabe am Serial-Monitor.
}

void sendTempValue(){
  // Call sensors.requestTemperatures() to issue a global temperature and Requests to all devices on the bus
  sensors.requestTemperatures(); 
  
  Serial.print("Temperature ");
  // Why "byIndex"? You can have more than one IC on the same bus. 0 refers to the first IC on the wire
  Serial.println(sensors.getTempCByIndex(0)); 
}

void loop(){
  // check if new messages are incoming
  if (1 && Serial.available() > 0){
      //digitalWrite(LED_BUILTIN, HIGH);
      int val = char(Serial.read()) - '0';
      if (val == 1){
        sendDiodeValue();
      }
      else if (val == 2){
        sendTempValue();
      }
      delay(200);
  }
}