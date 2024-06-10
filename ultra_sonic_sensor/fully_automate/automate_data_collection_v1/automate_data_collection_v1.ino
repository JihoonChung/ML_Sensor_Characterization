#include <NewPing.h>

// Stepper motor definitions and setup
const int stepPin = 3; // Stepper motor step pin
const int dirPin = 4; // Stepper motor direction pin
const int buttonPin = 2; // Button pin for reset
const int stepsPerRevolution = 200; // Steps per revolution for the motor
const float cmPerRevolution = 1.0; // Distance in cm per full revolution of the stepper motor
int currentPositionCm = 0; // Current position of the stepper motor in cm
bool buttonPressed = false;

// Ultrasonic sensor definitions and setup
#define TRIGGER_PIN  12  // Arduino pin tied to trigger pin on the ultrasonic sensor.
#define ECHO_PIN     9   // Arduino pin tied to echo pin on the ultrasonic sensor.
#define MAX_DISTANCE 200 // Maximum distance we want to ping for (in centimeters).

NewPing sonar(TRIGGER_PIN, ECHO_PIN, MAX_DISTANCE); // NewPing setup of pins and maximum distance.

const int numSamples = 200;
unsigned int samples[numSamples];
unsigned long sampleTimes[numSamples];
unsigned long delayBetweenPings = 16800; // Delay between pings in microseconds
bool delayInMicroseconds = true; // Default delay is in microseconds

void setup() {
  pinMode(stepPin, OUTPUT);
  pinMode(dirPin, OUTPUT);
  pinMode(buttonPin, INPUT_PULLUP);
  Serial.begin(9600);
  Serial.println("Stepper motor setup complete.");
}

void loop() {
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
  while (digitalRead(buttonPin) == HIGH) { // Adjusted logic for flipped input
    rotateStepper(int(0.1 * stepsPerRevolution), LOW); // Rotate forward
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

    samples[i] = uS;

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
    Serial.print(samples[i] / US_ROUNDTRIP_CM);
    Serial.print(",");
    Serial.print(samples[i]);
    Serial.print(",");
    Serial.print(currentPositionCm);
    Serial.print(",");
    Serial.println(delayBetweenPings);
  }
}

void runSequence() {
  const float positionsCm[] = {0, 5, 10, 15, 20, 30}; // Example positions in cm
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
  Serial.print("Delay updated to: ");
  Serial.println(delayBetweenPings);
}

void processCommand(String command) {
  if (command.length() > 0) {
    if (command == "reset") {
      Serial.println("Reset command received. Moving backward until button is pressed.");
      resetStepper();
    } else if (command == "run") {
      Serial.println("Run sequence command received.");
      runSequence();
    } else if (command.startsWith("D")) {
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
        } else if (directionChar == 'R' && buttonPressed) {
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
