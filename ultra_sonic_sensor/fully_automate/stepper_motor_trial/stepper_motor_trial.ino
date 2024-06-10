int stepPin = 3;
int dirPin = 2;
int buttonPin = 4; // Assuming the button is connected to pin 4
const int stepsPerRevolution = 200; // Adjust this value based on your stepper motor
bool buttonPressed = false;
bool lastButtonState = false;
unsigned long lastDebounceTime = 0; 
unsigned long debounceDelay = 50; // 50 milliseconds debounce time
long currentPosition = 0; // Track current position in steps

void setup() {
  pinMode(stepPin, OUTPUT);
  pinMode(dirPin, OUTPUT);
  pinMode(buttonPin, INPUT_PULLUP); // Set button pin as input with internal pull-up resistor
  Serial.begin(9600); // Start the Serial communication at 9600 baud rate
  Serial.println("Stepper motor control initialized.");
  Serial.println("Resetting");
  resetStepper();
  Serial.println("Type commands like 'F0.5' for forward rotation, 'R1.5' for reverse rotation, and 'reset' to reset the motor position.");
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
    String command = Serial.readStringUntil('\n'); // Read the incoming string
    Serial.print("Received command: ");
    Serial.println(command);
    processCommand(command);
  }
}

void processCommand(String command) {
  if (command.length() > 0) {
    if (command == "reset") {
      Serial.println("Reset command received. Moving backward until button is pressed.");
      resetStepper();
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
          currentPosition += steps; // Update current position
        } else if (directionChar == 'R' && !buttonPressed) {
          Serial.println("Rotating backward.");
          rotateStepper(steps, LOW); // Rotate backward if button is not pressed
          currentPosition -= steps; // Update current position
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
  while (buttonPressed) { // Adjusted logic for flipped input
    rotateStepper(int(0.1 * stepsPerRevolution), LOW); // Rotate forward
    buttonPressed = digitalRead(buttonPin); // Update button state
  }
  Serial.println("Reset complete, button pressed.");
  currentPosition = 0; // Reset position to zero
}
