
// d11 prawy d12 lewy

int motorSpeedPinR = 11; //Right motor speed
int motorSpeedPinL = 6; //Left motor speed

int trigPin = 9;      // trig pin of HC-SR04

int echoPin = 10;     // Echo pin of HC-SR04


int revleft4 = 4;       //Reverse motion of Left motor

int fwdleft5 = 5;       //Forward motion of Left motor

int revright6 = 7;      //Reverse motion of Right motor

int fwdright7 = 8;      //Forward motion of Right motor


long duration, distance;


void setup() {

  

  delay(random(500,2000));   // delay for random time

  Serial.begin(9600);

  pinMode(revleft4, OUTPUT);      // set Motor pins as output
  pinMode(fwdleft5, OUTPUT);

  pinMode(revright6, OUTPUT);
  pinMode(fwdright7, OUTPUT);

  pinMode(motorSpeedPinR, OUTPUT);
  pinMode(motorSpeedPinL, OUTPUT);

  pinMode(trigPin, OUTPUT);         // set trig pin as output

  pinMode(echoPin, INPUT);          //set echo pin as input to capture reflected waves


  analogWrite(motorSpeedPinR, 100);
  analogWrite(motorSpeedPinL, 125);


}


void loop() {



  digitalWrite(trigPin, LOW);

  delayMicroseconds(2);   

  digitalWrite(trigPin, HIGH);     // send waves for 10 us

  delayMicroseconds(10);

  duration = pulseIn(echoPin, HIGH); // receive reflected waves

  distance = duration / 58.2;   // convert to distance

  delay(10);

    // If you dont get proper movements of your robot then alter the pin numbers

  if (distance > 19)            

  {

    digitalWrite(fwdright7, HIGH);                    // move forward

    digitalWrite(revright6, LOW);

    digitalWrite(fwdleft5, HIGH);                                

    digitalWrite(revleft4, LOW);                                                       

  }


  if (distance < 18)

  {

    digitalWrite(fwdright7, LOW);  //Stop                

    digitalWrite(revright6, LOW);

    digitalWrite(fwdleft5, LOW);                                

    digitalWrite(revleft4, LOW);

    delay(500);

    digitalWrite(fwdright7, LOW);      //movebackword         

    digitalWrite(revright6, HIGH);

    digitalWrite(fwdleft5, LOW);                                

    digitalWrite(revleft4, HIGH);

    delay(500);

    digitalWrite(fwdright7, LOW);  //Stop                

    digitalWrite(revright6, LOW);

    digitalWrite(fwdleft5, LOW);                                

    digitalWrite(revleft4, LOW);  

    delay(100);  

    digitalWrite(fwdright7, HIGH);       

    digitalWrite(revright6, LOW);   

    digitalWrite(revleft4, LOW);                                 

    digitalWrite(fwdleft5, LOW);  

    delay(500);

  }


}