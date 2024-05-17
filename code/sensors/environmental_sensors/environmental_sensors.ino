// read the following sensors
// - 1 photodiode to observe room light 
// - several temperature sensors rated to 
//       -55°C with 9 bit precision (0.5°C above -10) taking 94 ms conversion time in parasite mode (faster in 5V supply mode)
//       resolutions: 9, 10, 11, 12 bit (0.5, 0.25, 0.125, 0.0625 precision above -10)
//        use 12 bit resolution so maybe 0.25 °C resolution down to -55°C
//        error values: -10x temperature too low; -200 device disconnected during operation


/*
Temperature sensors:
0 283023E70D00009A first after arduino
1 28E1F2E70D0000FA 2nd after arduino
2 285140E70D000031 4th after arduino
3 2817AFE60D0000CC 3rd after arduino


*/

// ------------------------------------------------------------
// for screen
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#define SCREEN_WIDTH 128  // OLED display width, in pixels
#define SCREEN_HEIGHT 64  // OLED display height, in pixels
// Declaration for an SSD1306 display connected to I2C (SDA, SCL pins)
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

// ------------------------------------------------------------
// for humidity
#include <DHT.h>
//Constants
#define DHTPIN 3     // what pin we're connected to
#define DHTTYPE DHT11   // DHT 11  (AM2302)
// Initialize DHT sensor for normal 16mhz Arduino
DHT dht(DHTPIN, DHTTYPE);
// ------------------------------------------------------------
// setup temperature sensor
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

int numberOfDevices; // Number of temperature devices found

DeviceAddress tempDeviceAddress; // We'll use this variable to store a found device address

int debug=0;
// ------------------------------------------------------------
// setup photodiode

int LDR = A2; // Analoger Pin als LDR Eingang
int sensorValue = 0; // Variable für den Sensorwert mit 0 als Startwert
int val=0; // for serial communication



// ------------------------------------------------------------
// functions for temperature sensor

// function to print a device address
void printAddress(DeviceAddress deviceAddress) {
  for (uint8_t i = 0; i < 8; i++) {
    if (deviceAddress[i] < 16) Serial.print("0");
      Serial.print(deviceAddress[i], HEX);
  }
}

float getTempValue(DeviceAddress deviceAddress){
  /*// Call sensors.requestTemperatures() to issue a global temperature and Requests to all devices on the bus
  sensors.requestTemperatures(); 
  
  Serial.print("Temperature ");
  // Why "byIndex"? You can have more than one IC on the same bus. 0 refers to the first IC on the wire
  Serial.println(sensors.getTempCByIndex(0));
  */
  float tempC = sensors.getTempC(deviceAddress);
  if (tempC == DEVICE_DISCONNECTED_C)
  {
    return -200;
  }
  return tempC;
}

void sendTempValue(){
  sensors.requestTemperatures(); // Send the command to get temperatures
  
  Serial.print("Temperatures: ");
  // Loop through each device, print out temperature data
  for(int i=0;i<numberOfDevices; i++) {
    // Search the wire for address
    if(sensors.getAddress(tempDeviceAddress, i)){
		
		// Output the device ID
		//Serial.print("Device: ");
		printAddress(tempDeviceAddress);
    Serial.print(" ");
    

    // Print the data
    float tempC = getTempValue(tempDeviceAddress);
    Serial.print(tempC);
    Serial.print("; ");
    } 	
  }
  Serial.println();
}

// ------------------------------------------------------------
// function for photodiode

float getDiodeValue(){
  sensorValue =analogRead(LDR); //
  float voltage = sensorValue * (5000.0 / 1023.0);
  return voltage;
}

void sendDiodeValue(){
  Serial.print("Diode ");
  Serial.println(getDiodeValue()); //Ausgabe am Serial-Monitor.
}
// ------------------------------------------------------------

void setup(){
  // *** start serial ********
  Serial.begin(9600);

  // *** check screen ********

  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {  // Address 0x3D for 128x64
    Serial.println(F("SSD1306 allocation failed"));
    for (;;)
      ;
  }
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.setCursor(0, 0);
  // Display static text
  display.println(F("Booting ..."));
  display.display();

  // *** humidity sensor 
  dht.begin();

  // *** start temperature sensors ****

  // search for boards
  // Start up the library
  sensors.begin();
  // get number of devices
  numberOfDevices = sensors.getDeviceCount();
  Serial.print("Found ");
  Serial.print(numberOfDevices, DEC);
  Serial.println(" devices.");

  // Loop through each device, print out address
  for(int i=0;i<numberOfDevices; i++) {
    if(sensors.getAddress(tempDeviceAddress, i)) {
        Serial.print("Found device ");
        Serial.print(i, DEC);
        Serial.print(" with address: ");
        printAddress(tempDeviceAddress);
        Serial.println();

        if (debug){
          // highest resolution is 12, should give 12
          //sensors.setResolution(tempDeviceAddress, 12);
          Serial.print("Device 0 Resolution: ");
          Serial.print(sensors.getResolution(tempDeviceAddress), DEC);
          Serial.println();
        }
    } else {
        Serial.print("Found ghost device at ");
        Serial.print(i, DEC);
        Serial.print(" but could not detect address. Check power and cabling");
    }
    
  }

  // for debugging temperature sensors
  if (debug){
      // report parasite power requirements
    // should be OFF
    Serial.print("Parasite power is: ");
    if (sensors.isParasitePowerMode()) Serial.println("ON");
    else Serial.println("OFF");

    
  }

  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.setCursor(0, 0);
  // Display static text
  display.println(F("Done booting!"));
  display.display();
}

void renewInfoOnScreen(int elapsedTime){

  display.clearDisplay();

  display.drawRect(0,0, display.width(), display.height()*0.8, SSD1306_WHITE);

  display.setTextSize(1);
  display.setTextColor(WHITE);
  int y=4;
  display.setCursor(8, y);
  // Display static text
  float light=getDiodeValue();
  display.print(F("Light:  "));
  if (light < 10){
    display.print(F("   "));
  }
  else if (light < 100){
    display.print(F("  "));
  }
  else if (light < 1000){
    display.print(F(" "));
  }
  display.print(light);
  display.println(F(" mV"));
  // ***
  y+=8;
  display.setCursor(8, y);
  display.print(F("Humidity: "));
  display.print(dht.readHumidity());
  display.println(F(" %"));
  y+=8;
  display.setCursor(8, y);
  display.print(F("H-Temp:   "));
  display.print(dht.readTemperature());
  display.println(F(" C"));
  y+=8+4;
  display.setCursor(8, y);
  display.print(F("Temps:"));
  // ***
  sensors.requestTemperatures(); // Send the command to get temperatures
  // Loop through each device, print out temperature data
  float tempC=-300;
  for(int i=0;i<numberOfDevices; i++) {
    if(sensors.getAddress(tempDeviceAddress, i)){
      tempC = getTempValue(tempDeviceAddress);
    }	
    else{
      tempC = -150;
    }

    display.print(tempC);
    if (i!=1 && i!=3){
      display.print(F(";"));
    }
    else if (i==1){
      y+=8;
      display.setCursor(44, y);
    }
  }
  y+=8;
  display.setCursor(8, y);
  display.println(".");
  // ***

  // display
  display.display();



  
}


// ------------------------------------------------------------
// variables for the loop
int elapsedTime=0;
int DELAY=200;

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
      else if (val == 3){
        Serial.print("Humidity ");
        Serial.print(dht.readHumidity());
        Serial.print("; Temperature ");
        Serial.print(dht.readTemperature());
        Serial.println("");
      }
      //delay(200);
  }

  if (elapsedTime>=2000){
    renewInfoOnScreen(elapsedTime);
    elapsedTime=0;
  }


  elapsedTime+=DELAY;
  delay(DELAY);
}