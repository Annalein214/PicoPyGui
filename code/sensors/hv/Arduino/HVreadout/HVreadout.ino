// PIN setup
int VmonPIN = A0; // Vmon
int EnablePIN = 2; // Enable pin on digital pin 2

// variables
int VmonValue = 0; // Variable für den Sensorwert mit 0 als Startwert
float Vmon = 0; // voltage value of Vmon
float hv = 0; // converted hv value of Vmon
String incomingMSG = ""; // gets incoming serial communication
float accuracy = 0; // calculate accuracy of hv

// constants
// constants
float monCoeff = 607.9; // measured
float monOffset=-28.9;
//float setCoeff = 623.7; // measured 
//float setOffset=1.5

float hvAcc = 0.005; // from datasheet
float arduinoAcc = 5000.0/1023.0 / 1000.0 ; // in V
// -------------------------------------------------------------------------

void setup(){
  Serial.begin(9600);
  
  pinMode(EnablePIN, OUTPUT);
  digitalWrite(EnablePIN, HIGH); // ensure being online

  delay(500);
}

// -------------------------------------------------------------------------

void loop(){

  /*
  if (1){ 
    // check if new messages are incoming
    // if msg 
    //    OFF -> turn off HV / pin2
    //    ON  -> turn on HV / pin2
    if (Serial.available() > 0){
      incomingMSG = Serial.readString();  //read until timeout
      incomingMSG.trim(); 
      if (incomingMSG == "ON") {
        // turn on HV
        digitalWrite(EnablePIN, HIGH);
        Serial.println("Enable HV");
        delay(500);
      }
      else if (incomingMSG == "OFF") {
        Serial.println("Disabled HV");
        // turn off HV
        digitalWrite(EnablePIN, LOW);
        delay(500);
      }
      else {
        Serial.print("ERROR: Don't understand message: ");
        Serial.println(incomingMSG);
        delay(500);
      }
    }
    

  }
*/

  if (1){
    // read Vmon
    VmonValue =analogRead(VmonPIN); //
    Vmon = VmonValue * (5000.0 / 1023.0); // 10 bit // -> mV
    hv =   Vmon * monCoeff / 1000.0 + monOffset ; // -> V
    accuracy = sqrt( sq(arduinoAcc * monCoeff) + sq(hvAcc*hv) ); // add in quadrature because uncertainties are not correlated, arduinoCoeff translated to HV before this
    Serial.print("\tVmon ");
    Serial.print(Vmon);
    Serial.print(" mV; HV "); 
    Serial.print(hv);
    Serial.print(" V +/- ");
    Serial.print(accuracy);
    Serial.print(" V");
    Serial.println("");
  }
  delay(500);
}