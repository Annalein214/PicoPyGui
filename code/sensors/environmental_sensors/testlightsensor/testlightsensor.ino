// only test the light sensor, nothing else
// After bootup send the value 1 via serial to get a response

int LDR = A6; // Analoger Pin als LDR Eingang
int sensorValue = 0; // Variable für den Sensorwert mit 0 als Startwert
int val=0; // for serial communication

void setup(){
  Serial.begin(9600);
  // Start up the library
}

void sendDiodeValue(){
  sensorValue =analogRead(LDR); //
  float voltage = sensorValue * (5000.0 / 1023.0);
  Serial.print("Diode ");
  Serial.println(voltage); //Ausgabe am Serial-Monitor.
}

void loop(){
  // check if new messages are incoming
  if (1 && Serial.available() > 0){
      //digitalWrite(LED_BUILTIN, HIGH);
      int val = char(Serial.read()) - '0';
      if (val == 1){
        sendDiodeValue();
      }
      delay(200);
  }
}

