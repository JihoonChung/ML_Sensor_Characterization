#include <NewPing.h>

// Stepper motor definitions and setup
const int stepPin = 3; // Stepper motor step pin
const int dirPin = 2; // Stepper motor direction pin
const int buttonPin = 5; // Button pin for reset
const int stepsPerRevolution = 262; // Steps per revolution for the motor
const float cmPerRevolution = 1.0; // Distance in cm per full revolution of the stepper motor
float currentPositionCm = 0; // Current position of the stepper motor in cm
bool buttonPressed = false; // this switch act oppositly
bool lastButtonState = false;
unsigned long lastDebounceTime = 0; 
unsigned long debounceDelay = 50; // 50 milliseconds debounce time

int totalLen = 53;

// Ultrasonic sensor definitions and setup
#define TRIGGER_PIN  12  // Arduino pin tied to trigger pin on the ultrasonic sensor.
#define ECHO_PIN     9   // Arduino pin tied to echo pin on the ultrasonic sensor.
#define MAX_DISTANCE 200 // Maximum distance we want to ping for (in centimeters).

NewPing sonar(TRIGGER_PIN, ECHO_PIN, MAX_DISTANCE); // NewPing setup of pins and maximum distance.

const int numSamples = 100;
unsigned long samples[numSamples];
unsigned long sampleTimes[numSamples];
unsigned long delayBetweenPings = 16800; // Delay between pings in microseconds
bool delayInMicroseconds = true; // Default delay is in microseconds

void setup() {
  pinMode(stepPin, OUTPUT);
  pinMode(dirPin, OUTPUT);
  pinMode(buttonPin, INPUT_PULLUP);
  Serial.begin(9600);
  //Serial.println("Stepper motor setup complete.");
  //Serial.println("Resetting");
  resetStepper();
  //Serial.println("Type commands like 'F0.5' for forward rotation, 'R1.5' for reverse rotation, and 'reset' to reset the motor position.");
}

void loop() {
  int reading = digitalRead(buttonPin); // Read the button state

  if (reading != lastButtonState) {
    lastDebounceTime = millis(); // Reset the debouncing timer
  }

  if ((millis() - lastDebounceTime) > debounceDelay) {
    if (reading != buttonPressed) {
      buttonPressed = reading;
      
      if (!buttonPressed) { // Adjusted logic for flipped input
        Serial.println("Button is pressed. Reverse rotation is disabled.");
      } else {
        Serial.println("Button is not pressed. Reverse rotation is enabled.");
      }
    }
  }

  lastButtonState = reading; // Update last button state
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    processCommand(command);
  }
}

void rotateStepper(int steps, int direction) {
  digitalWrite(dirPin, direction); // Set the direction
  for (int x = 0; x < steps; x++) {
    digitalWrite(stepPin, HIGH);
    delayMicroseconds(500);
    digitalWrite(stepPin, LOW);
    delayMicroseconds(500);
  }
  Serial.println("Rotation complete.");
}

void resetStepper() {
  digitalWrite(dirPin, LOW); // Set the direction to backward
  while (!buttonPressed) { // Adjusted logic for flipped input
    rotateStepper(int(0.1 * stepsPerRevolution), LOW); // Rotate forward
    buttonPressed = digitalRead(buttonPin); // Update button state
  }
  Serial.println("Reset complete, button pressed.");
  currentPositionCm = 0; // Reset position to zero
}

void moveStepperCm(float distanceCm, int direction) {
  int steps = int(distanceCm * stepsPerRevolution / cmPerRevolution);
  rotateStepper(steps, direction);
  currentPositionCm += (direction == HIGH ? distanceCm : -distanceCm);
}

void moveStepperSteps(int steps, int direction) {
  rotateStepper(steps, direction);
  currentPositionCm += (direction == HIGH ? float(steps) * cmPerRevolution / stepsPerRevolution : -float(steps) * cmPerRevolution / stepsPerRevolution);
}

// Ultrasonic sensor
void collectSamples() {
  // Reset sampleTimes array
  memset(sampleTimes, 0, sizeof(sampleTimes));

  for (int i = 0; i < numSamples; i++) {
    unsigned long startTime = micros();
    unsigned long uS = sonar.ping(); // Send ping, get ping time in microseconds (uS).

    samples[i] = (double)uS;

    if (delayInMicroseconds) {
      delayMicroseconds(delayBetweenPings); // Delay in microseconds
    } else {
      delay(delayBetweenPings); // Delay in milliseconds
    }
    unsigned long endTime = micros();
    unsigned long pingDuration = endTime - startTime;
    sampleTimes[i] = pingDuration;
  }
  printSamples();
  Serial.println("Sample collection complete.");
}

void printSamples() {
  for (int i = 0; i < numSamples; i++) {
    Serial.print(i);
    Serial.print(",");
    Serial.print(sampleTimes[i]);
    Serial.print(",");
    Serial.print((double)samples[i] / US_ROUNDTRIP_CM);
    Serial.print(",");
    Serial.print(samples[i]);
    Serial.print(",");
    Serial.print(totalLen-currentPositionCm);
    Serial.print(",");
    Serial.print(stepsPerRevolution*currentPositionCm);
    Serial.print(",");
    if (delayInMicroseconds){
      Serial.println(delayBetweenPings);
    }else{
      Serial.println(delayBetweenPings * 1000);
    }
  }
}

void runSequence() {
  const float positionsCm[] = {0,5,10,15,20,25,30,32,34,36,38,40}; // Example positions in cm
  const int numPositions = sizeof(positionsCm) / sizeof(positionsCm[0]);

  for (int i = 0; i < numPositions; i++) {
    float targetPositionCm = positionsCm[i];
    float distanceToMoveCm = targetPositionCm - currentPositionCm;

    if (distanceToMoveCm > 0) {
      moveStepperCm(distanceToMoveCm, HIGH);
    } else if (distanceToMoveCm < 0) {
      moveStepperCm(-distanceToMoveCm, LOW);
    }

    collectSamples();
  }
}


//---------------------------------------------------
// new automation 
//---------------------------------------------------

void printDelaySamples(unsigned long delay) {
  for (int i = 0; i < numSamples; i++) {
    Serial.print(i);
    Serial.print(",");
    Serial.print(sampleTimes[i]);
    Serial.print(",");
    Serial.print((double)samples[i] / US_ROUNDTRIP_CM);
    Serial.print(",");
    Serial.print(samples[i]);
    Serial.print(",");
    Serial.print(totalLen-currentPositionCm);
    Serial.print(",");
    Serial.print(stepsPerRevolution*currentPositionCm);
    Serial.print(",");
    Serial.println(delay);
  }
}

void runDelaySequence() {
  const float delays[] = {16800,10000,8000,6000,5000,3000,2000}; // delays in micro
  const int numDelays = sizeof(delays) / sizeof(delays[0]);

  for (int i = 0; i < numDelays; i++) {
    float targetDelay = delays[i];
    collectdelayedSamples(targetDelay);
  }
}

void collectdelayedSamples(unsigned long delay) {
  // Reset sampleTimes array
  memset(sampleTimes, 0, sizeof(sampleTimes));

  for (int i = 0; i < numSamples; i++) {
    unsigned long startTime = micros();
    unsigned long uS = sonar.ping(); // Send ping, get ping time in microseconds (uS).

    samples[i] = (double)uS;

    delayMicroseconds(delay); // Delay in microseconds

    unsigned long endTime = micros();
    unsigned long pingDuration = endTime - startTime;
    sampleTimes[i] = pingDuration;
  }
  printDelaySamples(delay);
  Serial.println("Sample collection complete.");
}


//---------------------------------------------------


void setDelay(char command) {
  if (command == 'M') {
    delayInMicroseconds = false;
    Serial.println("Delay set to milliseconds.");
  } else if (command == 'U') {
    delayInMicroseconds = true;
    Serial.println("Delay set to microseconds.");
  }
}

void updateDelay(unsigned long delay) {
  delayBetweenPings = delay;
  if (delayInMicroseconds){
    Serial.print("Delay updated to: ");
    Serial.print(delayBetweenPings);
    Serial.println(" us");
  }else{
    Serial.print("Delay updated to: ");
    Serial.print(delayBetweenPings);
    Serial.println(" ms");
  }
  
}


void processCommand(String command) {
  if (command.length() > 0) {
    if (command == "reset") {
      Serial.println("Reset command received. Moving backward until button is pressed.");
      resetStepper();
    } else if (command == "run") {
      Serial.println("Run motor sequence command received.");
      runSequence();
    } else if (command.startsWith("M")) {
      delayInMicroseconds = false;
      Serial.println("Delay set to milliseconds.");

    }else if (command == "P") { //new
      Serial.println("Run Delay sequence command received.");
      runDelaySequence();
    }
    else if (command.startsWith("U")) {
      delayInMicroseconds = true;
      Serial.println("Delay set to microseconds.");
    }
    else if (command.startsWith("D")) {
      unsigned long delay = command.substring(1).toInt();
      updateDelay(delay);
    } else {
      char directionChar = command[0];
      float rotations = command.substring(1).toFloat();

      if (rotations > 0) {
        int steps = int(rotations * stepsPerRevolution);
        Serial.print("Rotations: ");
        Serial.println(rotations);
        Serial.print("Steps: ");
        Serial.println(steps);

        if (directionChar == 'F') {
          Serial.println("Rotating forward.");
          rotateStepper(steps, HIGH); // Rotate forward
          currentPositionCm += float(steps) * cmPerRevolution / stepsPerRevolution; // Update current position in cm
        } else if (directionChar == 'R' && !buttonPressed) {
          Serial.println("Rotating backward.");
          rotateStepper(steps, LOW); // Rotate backward if button is not pressed
          currentPositionCm -= float(steps) * cmPerRevolution / stepsPerRevolution; // Update current position in cm
        } else if (directionChar == 'R' && !buttonPressed) {
          Serial.println("Cannot rotate backward, button is pressed.");
        } else {
          Serial.println("Invalid direction command.");
        }
      } else {
        Serial.println("Invalid rotation value.");
      }
    }
  }
}
