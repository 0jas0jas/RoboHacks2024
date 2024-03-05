#include <ArduinoJson-v7.0.3.h>
#include <rhComms.h>
#include "WiFi.h"
#include <ESP32Servo.h>

const char* ssid = "SustainaBot";
const char* password = "1234";

CarController controller;

Servo myservo;  // create servo object to control a servo



WiFiServer server(80);

#define MOTOR_A_IN1 12
#define MOTOR_A_IN2 14
#define MOTOR_B_IN3 32
#define MOTOR_B_IN4 13
#define MOTOR_A_ENA 21 // PWM for Motor A
#define MOTOR_B_ENB 25 // PWM for Motor B

// 16 servo objects can be created on the ESP32

int pos = 0;    // variable to store the servo position
// Recommended PWM GPIO pins on the ESP32 include 2,4,12-19,21-23,25-27,32-33 
// Possible PWM GPIO pins on the ESP32-S2: 0(used by on-board button),1-17,18(used by on-board LED),19-21,26,33-42
// Possible PWM GPIO pins on the ESP32-S3: 0(used by on-board button),1-21,35-45,47,48(used by on-board LED)
// Possible PWM GPIO pins on the ESP32-C3: 0(used by on-board button),1-7,8(used by on-board LED),9-10,18-21
int servoPin = 33;


void setup(){
  
	ESP32PWM::allocateTimer(0);
	ESP32PWM::allocateTimer(1);
	ESP32PWM::allocateTimer(2);
	ESP32PWM::allocateTimer(3);
	myservo.setPeriodHertz(50);    // standard 50 hz servo
	myservo.attach(servoPin, 1000, 2000); // attaches the servo on pin 18 to the servo object
	// using default min/max of 1000us and 2000us
	// different servos may require different min/max settings
	// for an accurate 0 to 180 sweep

  Serial.begin(115200);

  // set ESP32 LED pin to LOW
  // pinMode(2, OUTPUT);
  // digitalWrite(2, LOW);
  pinMode(MOTOR_A_IN1, OUTPUT);
  pinMode(MOTOR_A_IN2, OUTPUT);
  pinMode(MOTOR_B_IN3, OUTPUT);
  pinMode(MOTOR_B_IN4, OUTPUT);
  pinMode(MOTOR_A_ENA, OUTPUT);
  pinMode(MOTOR_B_ENB, OUTPUT);

  ledcSetup(0, 5000, 8);
  ledcSetup(1, 5000, 8);

  ledcAttachPin(MOTOR_A_ENA, 0);
  ledcAttachPin(MOTOR_B_ENB, 1);

  // digitalWrite(MOTOR_A_IN2, LOW);
  // digitalWrite(MOTOR_A_IN2, LOW);




  // start the wifi access point with the specified name and password
  WiFi.mode(WIFI_AP);
  WiFi.softAP(ssid);

  // set the CarController object's server reference to the server object
  controller.setServer(&server);

  // print the IP address of the ESP32 to the serial monitor
  Serial.print("IP Address of ESP32: ");
  Serial.println(WiFi.softAPIP());

  // start the server on port 80
  server.begin();
}



void loop(){

  if (controller.hasClient()) { //
    int read = controller.run();
    if (read == -1) {
      Serial.println("Error reading");
    } else {
      digitalWrite(2, controller.getValue("controlType", "Keyboard"));

      if (controller.getValue("keys", "UP") == 1){
      Serial.print("f");
      moveForward();
    }
    // Check for backward movement (DOWN arrow or S key)
    else if (controller.getValue("keys", "DOWN") == 1){
      Serial.print("b");
      moveBackward();
    }
    // Check for left turn (LEFT arrow or A key)
    else if (controller.getValue("keys", "LEFT") == 1){
      Serial.print("l");
      turnLeft();
    }
    // Check for right turn (RIGHT arrow or D key)
    else if (controller.getValue("keys", "RIGHT") == 1){
      
      turnRight();
    }
    // If no movement keys are pressed, stop the motors
    else {
      stopMotors();
    }



    // if (controller.getValue("keys", "S") == 0){
    //   Serial.print("life");
    //   if(pos > 0){
    //     myServo.write(pos);
    //     pos -= 10;
    //   }
    //   delay(15);
    // }
    }
  } else {
  Serial.println("Waiting for client...");
  while (controller.connectClient()) {}
  Serial.println("Connected to client!");
  }
  delay(50);
}

// void servo(){
// 	for (pos = 180; pos >= 0; pos -= 1) {
// 		myServo.write(pos);    
// 		delay(15);
// 	}
// }

void moveForward() {
  digitalWrite(MOTOR_A_IN1, LOW);
  digitalWrite(MOTOR_A_IN2, HIGH);
  digitalWrite(MOTOR_B_IN3, HIGH);
  digitalWrite(MOTOR_B_IN4, LOW);
  ledcWrite(0, 255);
  ledcWrite(1, 255);
}

void moveBackward() {
  digitalWrite(MOTOR_A_IN1, HIGH);
  digitalWrite(MOTOR_A_IN2, LOW);
  digitalWrite(MOTOR_B_IN3, LOW);
  digitalWrite(MOTOR_B_IN4, HIGH);
  ledcWrite(0, 255);
  ledcWrite(1, 255);
}

void turnLeft() {
  digitalWrite(MOTOR_A_IN1, HIGH);
  digitalWrite(MOTOR_A_IN2, LOW);
  digitalWrite(MOTOR_B_IN3, HIGH);
  digitalWrite(MOTOR_B_IN4, LOW);
  ledcWrite(0, 255); // Full speed Motor A
  ledcWrite(1, 255); // Full speed Motor B
}
void turnRight() {
  digitalWrite(MOTOR_A_IN1, LOW);
  digitalWrite(MOTOR_A_IN2, HIGH);
  digitalWrite(MOTOR_B_IN3, LOW);
  digitalWrite(MOTOR_B_IN4, HIGH);
  ledcWrite(0, 255); // Full speed Motor A
  ledcWrite(1, 255); // Full speed Motor B
}

void stopMotors() {
  digitalWrite(MOTOR_A_IN1, LOW);
  digitalWrite(MOTOR_A_IN2, LOW);
  digitalWrite(MOTOR_B_IN3, LOW);
  digitalWrite(MOTOR_B_IN4, LOW);
  ledcWrite(0, 0);
  ledcWrite(1, 0);
}
