# Ultrasonic Sensor Data Collection System

## Overview

This system allows you to collect data from an ultrasonic sensor connected to an Arduino and save the collected data into a CSV file using Python. The data includes measurements such as distance, timestamp, and user-defined metadata.

## Components

1. **Arduino Code**: Collects data from the ultrasonic sensor and sends it over the serial port.
2. **Python Script**: Reads the data from the serial port, prompts the user for metadata, and saves the data into a CSV file.

## Arduino Code

### Setup

1. **Connect the ultrasonic sensor** to your Arduino:
   - Trigger pin to Arduino pin 12
   - Echo pin to Arduino pin 9
   - VCC to 5V
   - GND to GND
2. **Upload the Arduino code** to your Arduino board.

### How to Use

1. Open the Arduino IDE.
2. Copy and paste the Arduino code into the IDE.
3. Verify and upload the code to your Arduino board.
4. Open the Serial Monitor from the Tools menu in the Arduino IDE.
5. Enter 'R' to start collecting samples, 'u' to increase delay, and 'd' to decrease delay between pings.

## Python Script

### Setup

1. **Install pyserial**:
   ```sh
   pip install pyserial
2. **Connect the Arduino** to your computer via USB.
3. **Adjust the serial port** in the Python script (change it to your specific port).

### How to Use

1. Open a text editor or IDE and create a new Python file.
2. Copy and paste the Python script into the file.
3. Save the file, e.g., `record_arduino_data.py`.
4. Open a terminal or command prompt.
5. Run the Python script:
    ```sh
    python record_arduino_data.py
    ```
6. **Enter metadata** when prompted.
7. **Enter a filename** for the current recording session when prompted.
8. **Enter 'R'** to start recording data from the Arduino. The script will save the data in a CSV file with the specified filename.
9. **Enter 'u' or 'd'** to change the delay between pings on the Arduino.
10. **Enter 'q'** to quit the script.

This system ensures that each recording session generates a separate CSV file with user-defined metadata and sensor data, allowing for easy management and analysis.
