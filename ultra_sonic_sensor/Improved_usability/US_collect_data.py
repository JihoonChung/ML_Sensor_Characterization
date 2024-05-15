import serial
import time
import csv

# Function to get user input for the additional attributes
def get_user_attributes():
    experiment_nm = input("Enter Experiment name: ")
    arduino_id = input("Enter Arduino ID: ")
    sensor_id = input("Enter Sensor ID: ")
    range_cm = input("Enter Range (cm): ")
    sensor_length = input("Enter Sensor length (cm): ")
    color_of_sensor = input("Enter Color of sensor: ")
    angle_xy = input("Enter Angle on XY plane: ")
    side_a = input("Enter Side a (cm): ")
    side_b = input("Enter Side b (cm): ")
    side_c = input("Enter Side c (cm): ")
    angle_yz = input("Enter Angle on YZ plane: ")
    sensor_configuration = input("Enter Sensor Configuration: ")
    sensor_angle = input("Enter Sensor Angle: ")
    surface_material = input("Enter Surface material: ")
    surface_length = input("Enter Surface Length (cm): ")
    surface_width = input("Enter Surface Width (cm): ")

    return {
        "Experiment Name": experiment_nm,
        "Arduino ID": arduino_id,
        "Sensor ID": sensor_id,
        "Range (cm)": range_cm,
        "Sensor length (cm)": sensor_length,
        "Color of sensor": color_of_sensor,
        "Angle on XY plane": angle_xy,
        "Side a (cm)": side_a,
        "Side b (cm)": side_b,
        "Side c (cm)": side_c,
        "Angle on YZ plane": angle_yz,
        "Sensor Configuration": sensor_configuration,
        "Sensor Angle": sensor_angle,
        "Surface material": surface_material,
        "Surface Length (cm)": surface_length,
        "Surface Width (cm)": surface_width
    }

# Get user attributes
attributes = get_user_attributes()

# Set up the serial connection
ser = serial.Serial('/dev/cu.usbserial-120', 9600)  
time.sleep(2)  # Give some time for the connection to be established

# Open a CSV file for writing
csv_filename = f'ultra_sonic_sensor/Improved_usability/data_collection/ultrasonic_data_{attributes["Experiment Name"]}.csv'
with open(csv_filename, 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    # Write the header
    csvwriter.writerow([
        'Arduino ID', 'Sensor ID', 'Trial', 'Range (cm)', 'Start Time (ms)',
        'Distance (cm)', 'Echo Return Time (us)', 'Sensor length (cm)', 'Delay (ms)',
        'Color of sensor', 'Angle on XY plane', 'Side a (cm)', 'Side b (cm)', 'Side c (cm)',
        'Angle on YZ plane', 'Sensor Configuration', 'Sensor Angle', 'Surface material',
        'Surface Length (cm)', 'Surface Width (cm)'
    ])

    start_time = time.time() * 1000  # Start time in milliseconds

    print("Type 'exit' and press Enter to stop the data collection.")
    
    delay_between_pings = 10  # Initial delay between pings

    while True:
        # Get user input for commands
        user_input = input("Enter command (R, up, down, exit): ").strip().lower()
        if user_input == 'exit':
            break
        elif user_input in ['r', 'up', 'down']:
            print(f"Sending command: {user_input}")  # Debugging statement
            ser.write(user_input.encode())  # Send command to Arduino
            time.sleep(2)  # Add a delay to allow Arduino to process the command and send data

            if user_input == 'r':
                # Read and process data from Arduino
                data_lines = []
                while True:
                    if ser.in_waiting > 0:
                        line = ser.readline().decode('utf-8').strip()
                        print(f"Received data: {line}")  # Debugging statement
                        if line == "Sample collection complete.":
                            print("Sample collection complete.")
                            break  # Stop collecting if the Arduino signals completion

                    if len(data_lines) >= 100:
                        print("Collected 100 samples.")
                        break  # Ensure we collect 100 samples

                for i, data in enumerate(data_lines):
                    parts = data.split(',')
                    if len(parts) == 2:  # Ensure correct number of elements received
                        timestamp = parts[0]
                        ping_time = parts[1]
                        distance = float(ping_time) / 58.0  # Convert ping time to distance in cm
                        trial = i + 1
                        csvwriter.writerow([
                            attributes['Arduino ID'], attributes['Sensor ID'], trial, attributes['Range (cm)'],
                            timestamp, distance, ping_time, attributes['Sensor length (cm)'],
                            delay_between_pings, attributes['Color of sensor'], attributes['Angle on XY plane'],
                            attributes['Side a (cm)'], attributes['Side b (cm)'], attributes['Side c (cm)'],
                            attributes['Angle on YZ plane'], attributes['Sensor Configuration'],
                            attributes['Sensor Angle'], attributes['Surface material'],
                            attributes['Surface Length (cm)'], attributes['Surface Width (cm)']
                        ])
                print("Finished writing data to CSV.")

        # Handle delay adjustment commands
        if user_input == 'up':
            if delay_between_pings < 20:
                delay_between_pings += 1
                print(f"Delay between pings increased to: {delay_between_pings} ms")
            else:
                print("Delay is already at maximum (20 ms)")
        elif user_input == 'down':
            if delay_between_pings > 5:
                delay_between_pings -= 1
                print(f"Delay between pings decreased to: {delay_between_pings} ms")
            else:
                print("Delay is already at minimum (5 ms)")

ser.close()
print(f'Data saved to {csv_filename}')
