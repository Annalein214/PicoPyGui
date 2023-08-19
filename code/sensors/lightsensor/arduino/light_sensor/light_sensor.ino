int LDR = A0; // Analoger Pin als LDR Eingang
int sensorValue = 0; // Variable für den Sensorwert mit 0 als Startwert
int val=0;


void setup(){
  Serial.begin(9600);
}

void sendValue(){
  sensorValue =analogRead(LDR); //
  float voltage = sensorValue * (5000.0 / 1023.0);
  Serial.print("Diode ");
  Serial.println(voltage); //Ausgabe am Serial-Monitor.
}

void loop(){

  // check if new messages are incoming
  if (Serial.available() > 0){
      digitalWrite(LED_BUILTIN, HIGH);
      int val = char(Serial.read()) - '0';
      if (val == 1){
        sendValue();
      }
      delay(200);
  }
}