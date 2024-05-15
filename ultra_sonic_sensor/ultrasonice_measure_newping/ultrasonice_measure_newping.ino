#include <NewPing.h>

#define TRIGGER_PIN  12  // Arduino pin tied to trigger pin on the ultrasonic sensor.
#define ECHO_PIN     9  // Arduino pin tied to echo pin on the ultrasonic sensor.
#define MAX_DISTANCE 200 // Maximum distance we want to ping for (in centimeters).

NewPing sonar(TRIGGER_PIN, ECHO_PIN, MAX_DISTANCE); // NewPing setup of pins and maximum distance.

void setup() {
  Serial.begin(9600); // Open serial connection at 9600 baud to output the distance.
}

void loop() {
  unsigned int uS = sonar.ping(); // Send ping, get ping time in microseconds (uS).
  float distance = uS / US_ROUNDTRIP_CM; // Convert time into distance.
  
  // Print the results in a CSV format: milliseconds since start, distance in cm, echo return time 
  Serial.print(millis());
  Serial.print(",");
  Serial.print(distance);
  Serial.print(",");
  Serial.println(uS);

  //. maybe we can measure it by adjusting frequency or puls duration 
  delay(1000); // Delay a second before next ping.
}
