// Define pin numbers for the ultrasonic sensor
const int triggerPin = 12;
const int echoPin = 9;

// Define variables for the duration and the distance
long duration;
int distance;

void setup() {
  // Initialize Serial communication at 9600 baud rate
  Serial.begin(9600);
  
  // Set the trigger pin as an output and the echo pin as an input
  pinMode(triggerPin, OUTPUT);
  pinMode(echoPin, INPUT);
}

void loop() {
  // Clear the trigger pin
  digitalWrite(triggerPin, LOW);
  delayMicroseconds(2);
  
  // Sets the trigger pin to HIGH state for 10 microseconds
  digitalWrite(triggerPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(triggerPin, LOW);
  
  // Reads the echo pin, returns the sound wave travel time in microseconds
  duration = pulseIn(echoPin, HIGH);
  
  // Calculate the distance
  distance = duration * 0.034 / 2; // Speed of sound wave divided by 2 (go and return)
  
  // Print the distance on the Serial Monitor
  Serial.print("Distance: ");
  Serial.print(distance);
  Serial.println(" cm");
  
  // Delay 500 milliseconds before the next measurement
  delay(500);
}
