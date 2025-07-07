/*
This script can drive 2 HV devices right now
- provides ON switch for HV on digital pin
- provides HV read # TODO switch to picoscope?
*/

// PIN setup
int VmonPIN1 = A0; // Vmon
int VmonPIN2 = A7; // Vmon
int VmonPIN =VmonPIN1; // preselect 1

int MiniPIN = 4; // enable digital pin 4
int MacroPIN = 6;
const int MAXPRESS = 14;
unsigned long pressTimes[MAXPRESS];
int head=0;
int count=0;
int laststate = 1;
unsigned long lastDebounceTime =0;
const unsigned long debounceDelay=100; // milliseconds
int lastSentIndex=0;

unsigned long pressTimes2[MAXPRESS];
int head2=0;
int count2=0;
int lastSentIndex2=0;
int laststate2 = 1;
unsigned long lastDebounceTime2 =0;


int EnablePIN1 = 2; // Enable pin on digital pin 2
int EnablePIN2 = 3; // Enable pin on digital pin 2

// constants for voltage conversion
float monCoeff1 = 607.9; // measured
float monOffset1=-28.9;

float monCoeff = monCoeff1;
float monCoeff2 = monCoeff1; // measured
float monOffset2=-monOffset2;
float monOffset=monOffset1;

float hvAcc = 0.005; // from datasheet
float arduinoAcc = 5000.0/1023.0 / 1000.0 ; // in V
// -------------------------------------------------------------------------

void setup(){
  Serial.begin(115200);
  
  pinMode(EnablePIN1, OUTPUT);
  digitalWrite(EnablePIN1, HIGH); // New: ensure being online, could also be used to switch on/off manually

  pinMode(EnablePIN2, OUTPUT);
  digitalWrite(EnablePIN2, HIGH); // New: ensure being online, could also be used to switch on/off manually

  pinMode(MiniPIN, INPUT);
    pinMode(MacroPIN, INPUT);


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

  ///////////// 
  bool state = digitalRead(MiniPIN);
  unsigned long now = millis();

  if (state == 0 && laststate == 1 && (now - lastDebounceTime)>debounceDelay){
    lastDebounceTime = now;
    pressTimes[head]=millis();
    head = (head + 1) % MAXPRESS;
    if (count < MAXPRESS) {
      count++;
    }
    else{
      if (lastSentIndex == head){
         lastSentIndex = (lastSentIndex +1)%MAXPRESS;
      }
    }

  }
  laststate = state;
  
  ///////////////////////////////////////////

  bool state2 = digitalRead(MacroPIN);

  if (state2 == 0 && laststate2 == 1 && (now - lastDebounceTime2)>debounceDelay){
    lastDebounceTime2 = now;
    pressTimes2[head2]=millis();
    head2 = (head2 + 1) % MAXPRESS;
    if (count2 < MAXPRESS) {
      count2++;
    }
    else{
      if (lastSentIndex2 == head2){
         lastSentIndex2 = (lastSentIndex2 +1)%MAXPRESS;
      }
    }

  }
  laststate2 = state2;

  ////////////////////////////////////////

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
      else if (val == 3){
        //int unreadCount = (head - lastSentIndex + MAXPRESS)%MAXPRESS;
        //int unreadCount = (head - count +i + MAXPRESS)% MAXPRESS;
        Serial.print("SW-MICRO:");
        //Serial.print(unreadCount);
        //Serial.print(":");
        Serial.print(count);
        Serial.print(":");

        for (int i =0; i<count; i++){
          int index = (head-count+i+MAXPRESS)%MAXPRESS;
          Serial.print(pressTimes[index]);
          Serial.print(",");
        }
        Serial.println(".");
        //lastSentIndex=(lastSentIndex + unreadCount)%MAXPRESS;
      }

      else if (val == 4){
        //int unreadCount2 = (head2 - lastSentIndex2 + MAXPRESS)%MAXPRESS;
        //int unreadCount = (head - count +i + MAXPRESS)% MAXPRESS;
        Serial.print("SW-MACRO:");
        //Serial.print(unreadCount2);
        //Serial.print(":");
        Serial.print(count2);
        Serial.print(":");

        for (int i =0; i<count; i++){
          int index2 = (head-count+i+MAXPRESS)%MAXPRESS;
          Serial.print(pressTimes2[index2]);
          Serial.print(",");
        }
        Serial.println(".");
        //lastSentIndex2=(lastSentIndex2 + unreadCount2)%MAXPRESS;
      }
      delay(200);
  }  
}
