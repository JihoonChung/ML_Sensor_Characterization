#include <NewPing.h>

#define TRIGGER_PIN  12  // Arduino pin tied to trigger pin on the ultrasonic sensor.
#define ECHO_PIN     9  // Arduino pin tied to echo pin on the ultrasonic sensor.
#define MAX_DISTANCE 100 // Maximum distance we want to ping for (in centimeters).

NewPing sonar(TRIGGER_PIN, ECHO_PIN, MAX_DISTANCE); // NewPing setup of pins and maximum distance.

const int numSamples = 100;
unsigned int samples[numSamples];
unsigned long sampleTimes[numSamples];
int delayBetweenPings = 10; // Delay between pings in milliseconds

void setup() {
  Serial.begin(9600); // Open serial connection at 9600 baud to output the distance.
  Serial.println("Enter 'R' to collect 100 samples or use 'up' and 'down' to change delay between pings.");
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
    unsigned int uS = sonar.ping(); // Send ping, get ping time in microseconds (uS).
    float distance = uS / US_ROUNDTRIP_CM; // Convert time into distance.
    samples[i] = uS;
    sampleTimes[i] = millis();
    delay(delayBetweenPings); // Delay before next ping.
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
    delayBetweenPings += 1;
    Serial.print("Delay between pings increased to: ");
    Serial.print(delayBetweenPings);
    Serial.println(" ms");
  } else {
    Serial.println("Delay is already at maximum (20 ms)");
  }
}

void decreaseDelay() {
  if (delayBetweenPings > 5) {
    delayBetweenPings -= 1;
    Serial.print("Delay between pings decreased to: ");
    Serial.print(delayBetweenPings);
    Serial.println(" ms");
  } else {
    Serial.println("Delay is already at minimum (5 ms)");
  }
}
