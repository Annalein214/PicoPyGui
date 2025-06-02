/*
This script can drive 2 HV devices right now
- provides ON switch for HV on digital pin
- provides HV read # TODO switch to picoscope?
*/

// PIN setup
int VmonPIN1 = A0; // Vmon
int VmonPIN2 = A7; // Vmon
int VmonPIN =VmonPIN1; // preselect 1

int EnablePIN1 = 2; // Enable pin on digital pin 2
int EnablePIN2 = 3; // Enable pin on digital pin 2

// constants for voltage conversion
float monCoeff1 = 607.9; // measured
float monOffset1=-28.9;1

float monCoeff = monCoeff1;
float monCoeff2 = monCoeff1; // measured
float monOffset2=-monOffset2;
float monOffset=monOffset1;

float hvAcc = 0.005; // from datasheet
float arduinoAcc = 5000.0/1023.0 / 1000.0 ; // in V
// -------------------------------------------------------------------------

void setup(){
  Serial.begin(9600);
  
  pinMode(EnablePIN1, OUTPUT);
  digitalWrite(EnablePIN1, HIGH); // New: ensure being online, could also be used to switch on/off manually

  pinMode(EnablePIN2, OUTPUT);
  digitalWrite(EnablePIN2, HIGH); // New: ensure being online, could also be used to switch on/off manually

  delay(500);
}

void sendValue(int devicenumber){

    if (devicenumber == 1){
      VmonPIN=VmonPIN1;
      monCoeff=monCoeff1;
      monOffset=monOffset1;
    }
    else {
      VmonPIN=VmonPIN2;
      monCoeff=monCoeff2;
      monOffset=monOffset2;
    }

    // read Vmon
    int VmonValue =analogRead(VmonPIN); //
    float Vmon = VmonValue * (5000.0 / 1023.0); // 10 bit // -> mV
    float hv =   Vmon * monCoeff / 1000.0 + monOffset ; // -> V
    float accuracy = sqrt( sq(arduinoAcc * monCoeff) + sq(hvAcc*hv) ); // add in quadrature because uncertainties are not correlated, arduinoCoeff translated to HV before this
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
        sendValue(1);
      }
      else if (val == 2){
        sendValue(2);
      }
      delay(200);
  }  
}