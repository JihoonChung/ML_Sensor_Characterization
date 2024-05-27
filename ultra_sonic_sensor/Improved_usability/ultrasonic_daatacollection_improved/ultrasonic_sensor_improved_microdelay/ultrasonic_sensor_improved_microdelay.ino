#include <NewPing.h>

#define TRIGGER_PIN  12  // Arduino pin tied to trigger pin on the ultrasonic sensor.
#define ECHO_PIN     9  // Arduino pin tied to echo pin on the ultrasonic sensor.
#define MAX_DISTANCE 100 // Maximum distance we want to ping for (in centimeters).

NewPing sonar(TRIGGER_PIN, ECHO_PIN, MAX_DISTANCE); // NewPing setup of pins and maximum distance.

const int numSamples = 200;
unsigned int samples[numSamples];
unsigned long sampleTimes[numSamples];
double delayBetweenPings = 16000; // Delay between pings in microseconds

void setup() {
  Serial.begin(9600); // Open serial connection at 9600 baud to output the distance.
}

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read();
    if (command == 'R') {
      collectSamples();
    } else if (command == 'u') {
      increaseDelay();
    } else if (command == 'd') {
      decreaseDelay();
    }
  }
}

void collectSamples() {
  // Reset sampleTimes array
  memset(sampleTimes, 0, sizeof(sampleTimes));

  for (int i = 0; i < numSamples; i++) {
    unsigned long startTime = micros();
    unsigned int uS = sonar.ping(); // Send ping, get ping time in microseconds (uS).
    unsigned long endTime = micros();
    unsigned long pingDuration = endTime - startTime;

    samples[i] = uS;
    sampleTimes[i] = pingDuration;
    delayMicroseconds(delayBetweenPings); // Delay before next ping.
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
    Serial.println(delayBetweenPings);
  }
}

void increaseDelay() {
  if (delayBetweenPings < 20) {
    delayBetweenPings += 0.1;
    Serial.print("Delay between pings increased to: ");
    Serial.print(delayBetweenPings);
    Serial.println(" us");
  } else {
    Serial.println("Delay is already at maximum (20 us)");
  }
}

void decreaseDelay() {
  if (delayBetweenPings > 0) {
    delayBetweenPings -= 0.1;
    Serial.print("Delay between pings decreased to: ");
    Serial.print(delayBetweenPings);
    Serial.println(" us");
  } else {
    Serial.println("Delay is already at minimum (0 us)");
  }
}
