Ultrasonic Sensor Data Collection System
Overview
This system allows you to collect data from an ultrasonic sensor connected to an Arduino and save the collected data into a CSV file using Python. The data includes measurements such as distance, timestamp, and user-defined metadata.

Components
Arduino Code: Collects data from the ultrasonic sensor and sends it over the serial port.
Python Script: Reads the data from the serial port, prompts the user for metadata, and saves the data into a CSV file.
Arduino Code
Setup
Connect the ultrasonic sensor to your Arduino:
Trigger pin to Arduino pin 12
Echo pin to Arduino pin 9
VCC to 5V
GND to GND
Upload the Arduino code to your Arduino board.
How to Use
Open the Arduino IDE.
Copy and paste the Arduino code into the IDE.
Verify and upload the code to your Arduino board.
Open the Serial Monitor from the Tools menu in the Arduino IDE.
Enter 'R' to start collecting samples, 'u' to increase delay, and 'd' to decrease delay between pings.
Python Script
Setup
Install pyserial:
sh
Copy code
pip install pyserial
Connect the Arduino to your computer via USB.
Adjust the serial port in the Python script (change 'COM3' to your specific port).
How to Use
Open a text editor or IDE and create a new Python file.
Copy and paste the Python script into the file.
Save the file, e.g., record_arduino_data.py.
Open a terminal or command prompt.
Run the Python script:
sh
Copy code
python record_arduino_data.py
Enter metadata when prompted.
Enter a filename for the current recording session when prompted.
Enter 'R' to start recording data from the Arduino. The script will save the data in a CSV file with the specified filename.
Enter 'u' or 'd' to change the delay between pings on the Arduino.
Enter 'q' to quit the script.
This system ensures that each recording session generates a separate CSV file with user-defined metadata and sensor data, allowing for easy management and analysis.