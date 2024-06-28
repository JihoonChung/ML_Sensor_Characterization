#include <NewPing.h>

#define TRIGGER_PIN  12  // Arduino pin tied to trigger pin on the ultrasonic sensor.
#define ECHO_PIN     9  // Arduino pin tied to echo pin on the ultrasonic sensor.
#define MAX_DISTANCE 200 // Maximum distance we want to ping for (in centimeters).

NewPing sonar(TRIGGER_PIN, ECHO_PIN, MAX_DISTANCE); // NewPing setup of pins and maximum distance.

const int numSamples = 200;
unsigned int samples[numSamples];
unsigned long sampleTimes[numSamples];
unsigned long delayBetweenPings = 16800; // Delay between pings in microseconds
bool delayInMicroseconds = true; // Default delay is in microseconds

void setup() {
  Serial.begin(9600); // Open serial connection at 9600 baud to output the distance.
}

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read();
    if (command == 'R') {
      collectSamples();
    } else if (command == 'M' || command == 'U') {
      setDelay(command);
    } else if (command == 'S') {
      runSequence();
    }
  }
}

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
    Serial.print(delayBetweenPings);
    if (delayInMicroseconds) {
      Serial.println(" us");
    } else {
      Serial.println(" ms");
    }
  }
}

void setDelay(char unit) {
  while (Serial.available() == 0) {
    // Wait for the user to input the delay value
  }
  int delayValue = Serial.parseInt();
  if (unit == 'M') {
    // If the unit is milliseconds
    delayBetweenPings = delayValue;
    delayInMicroseconds = false;
  } else if (unit == 'U') {
    // If the unit is microseconds
    delayBetweenPings = delayValue;
    delayInMicroseconds = true;
  }
  Serial.print("Delay between pings set to: ");
  Serial.print(delayBetweenPings);
  Serial.print(" ");
  Serial.println(unit == 'M' ? "milliseconds" : "microseconds");
}

void runSequence() {
  for (unsigned long delayValue = 400; delayValue <= 1000; delayValue += 50) {
    Serial.print("Running sequence with delay: ");
    Serial.print(delayValue);
    Serial.println(" microseconds");

    // Reset sampleTimes array
    memset(sampleTimes, 0, sizeof(sampleTimes));

    for (int i = 0; i < 100; i++) {
      unsigned long startTime = micros();
      unsigned long uS = sonar.ping(); // Send ping, get ping time in microseconds (uS).

      samples[i] = uS;

      delayMicroseconds(delayValue); // Delay in microseconds
      unsigned long endTime = micros();
      unsigned long pingDuration = endTime - startTime;
      sampleTimes[i] = pingDuration;
    }

    // Print samples for this delay
    for (int i = 0; i < 100; i++) {
      Serial.print(i);
      Serial.print(",");
      Serial.print(sampleTimes[i]);
      Serial.print(",");
      Serial.print(samples[i] / US_ROUNDTRIP_CM);
      Serial.print(",");
      Serial.print(samples[i]);
      Serial.print(",");
      Serial.print(delayValue);
      Serial.println(" us");
    }
    Serial.println("Sequence step complete.");
    delay(20); // put delay so each measurement are stable 
  }
  Serial.println("Run sequence complete.");
}