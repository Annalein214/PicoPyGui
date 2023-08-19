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
  digitalWrite(EnablePIN, HIGH); // New: ensure being online, could also be used to switch on/off manually

  delay(500);
}

void sendValue(){
    // read Vmon
    VmonValue =analogRead(VmonPIN); //
    Vmon = VmonValue * (5000.0 / 1023.0); // 10 bit // -> mV
    hv =   Vmon * monCoeff / 1000.0 + monOffset ; // -> V
    accuracy = sqrt( sq(arduinoAcc * monCoeff) + sq(hvAcc*hv) ); // add in quadrature because uncertainties are not correlated, arduinoCoeff translated to HV before this
    Serial.print("\tVmon "); // do not change this output! otherwise python receiver will break
    Serial.print(Vmon);
    Serial.print(" mV; HV "); 
    Serial.print(hv);
    Serial.print(" V +/- ");
    Serial.print(accuracy);
    Serial.print(" V");
    Serial.println("");
  }

// -------------------------------------------------------------------------

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