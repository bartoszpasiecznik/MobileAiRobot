int motorSpeedPinR = 11; //Right motor speed
int motorSpeedPinL = 6; //Left motor speed

int trigPin = 9;      // trig pin of HC-SR04

int echoPin = 10;     // Echo pin of HC-SR04


int revleft4 = 4;       //Reverse motion of Left motor

int fwdleft5 = 5;       //Forward motion of Left motor

int revright6 = 7;      //Reverse motion of Right motor

int fwdright7 = 8;      //Forward motion of Right motor


long duration, distance;
String command;


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
  analogWrite(motorSpeedPinL, 100);


}

void loop(){

  if (Serial.available()){
    command = Serial.readStringUntil('\n');
    command.trim();

    if (command.equals("forward")){
      Serial.println("Moving Forward");
      digitalWrite(fwdright7, HIGH);                    // move forward

      digitalWrite(revright6, LOW);

      digitalWrite(fwdleft5, HIGH);                                

      digitalWrite(revleft4, LOW); 
      
    }

    else if (command.equals("backward")){
      Serial.println("Moving Backward");
      digitalWrite(fwdright7, LOW);      //movebackword         

      digitalWrite(revright6, HIGH);

      digitalWrite(fwdleft5, LOW);                                

      digitalWrite(revleft4, HIGH);
      
    }

    else if (command.equals("left")){
      Serial.println("Moving Left");
      digitalWrite(fwdright7, LOW);                    // move left

      digitalWrite(revright6, LOW);

      digitalWrite(fwdleft5, HIGH);                                

      digitalWrite(revleft4, HIGH); 
      
    }

    else if (command.equals("right")){
      Serial.println("Moving Right");
      digitalWrite(fwdright7, HIGH);                    // move right

      digitalWrite(revright6, HIGH);

      digitalWrite(fwdleft5, LOW);                                

      digitalWrite(revleft4, LOW); 
      
    }

    else if (command.equals("stop")){
      Serial.println("STOPPING");
      digitalWrite(fwdright7, LOW);  //Stop                

      digitalWrite(revright6, LOW);

      digitalWrite(fwdleft5, LOW);                                

      digitalWrite(revleft4, LOW);
      
    }

    else{
      Serial.println("Wrong command");
      digitalWrite(fwdright7, LOW);  //Stop                

      digitalWrite(revright6, LOW);

      digitalWrite(fwdleft5, LOW);                                

      digitalWrite(revleft4, LOW);

    }
  }
}