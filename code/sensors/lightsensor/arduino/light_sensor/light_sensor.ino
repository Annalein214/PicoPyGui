int LDR = A0; // Analoger Pin als LDR Eingang
int sensorValue = 0; // Variable für den Sensorwert mit 0 als Startwert

void setup(){
  Serial.begin(9600);
}

void loop(){
  sensorValue =analogRead(LDR); //
  float voltage = sensorValue * (5000.0 / 1023.0);
  Serial.print("Diode ");
  Serial.println(voltage); //Ausgabe am Serial-Monitor.
}