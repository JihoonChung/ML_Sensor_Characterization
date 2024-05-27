import serial
import time
import csv

# Set up the serial connection (adjust '/dev/cu.usbserial-120' to your specific port)
ser = serial.Serial('/dev/cu.usbserial-120', 9600, timeout=1)

# Give the connection a second to settle
time.sleep(2)

# Function to prompt user for metadata
def get_user_defined_metadata():
    metadata = {
        "Arduino ID": input("Enter Arduino ID: "),
        "Sensor ID": input("Enter Sensor ID: "),
        "Range (cm)": input("Enter Range (cm): "),
        #"Sensor length (cm)": input("Enter Sensor length (cm): "),
        #"Color of sensor": input("Enter Color of sensor: "),
        #"Angle on XY plane": input("Enter Angle on XY plane: "),
        #"side a (cm)": input("Enter side a (cm): "),
        #"side b (cm)": input("Enter side b (cm): "),
        #"side c (cm)": input("Enter side c (cm): "),
        #"Angle on YZ plane": input("Enter Angle on YZ plane: "),
        #"Sensor Configuration": input("Enter Sensor Configuration: "),
        #"Sensor Angle": input("Enter Sensor Angle: "),
        #"Surface material": input("Enter Surface material: "),
        #"Surface Length (cm)": input("Enter Surface Length (cm): "),
        #"Surface Width (cm)": input("Enter Surface Width (cm): ")
    }
    return metadata

# Function to prompt user for filename
def get_filename():
    filename = input("Enter the filename for this session (without extension): ")
    return f"ultra_sonic_sensor/Improved_usability/data_collection_v3/US_data_{filename}.csv"

# Function to record data
def record_data(metadata, output_file):
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = [
            'Trial', 'Ping Duration', 'Distance (cm)', 'Ping Time (us)', 'Delay',
            'Arduino ID', 'Sensor ID', 'Range (cm)', 'Sensor length (cm)', 'Color of sensor', 
            'Angle on XY plane', 'side a (cm)', 'side b (cm)', 'side c (cm)', 
            'Angle on YZ plane', 'Sensor Configuration', 'Sensor Angle', 
            'Surface material', 'Surface Length (cm)', 'Surface Width (cm)'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        while True:
            line = ser.readline().decode('utf-8').strip()
            if line:
                print(line)
                data = line.split(',')
                if len(data) == 5:  # Ensure we have all the parts of the data
                    row = {
                        'Trial': data[0],
                        'Ping Duration': data[1],
                        'Distance (cm)': data[2],
                        'Ping Time (us)': data[3],
                        'Delay': data[4],
                    }
                    row.update(metadata)
                    writer.writerow(row)
            else:
                break

# Function to send commands to the Arduino
def send_command(command):
    ser.write(command.encode())

try:
    while True:
        user_input = input("Enter 'R' to record, 'M' to set delay in milliseconds, 'U' to set delay in microseconds, or 'q' to quit: ")
        if user_input.lower() == 'q':
            break
        elif user_input in ['R', 'M', 'U']:
            send_command(user_input)
            if user_input.lower() == 'r':
                filename = get_filename()
                metadata = get_user_defined_metadata()
                record_data(metadata, filename)
            elif user_input in ['M', 'U']:
                delay_value = input(f"Enter the delay value in {'milliseconds' if user_input == 'M' else 'microseconds'}: ")
                send_command(delay_value)
                line = ser.readline().decode('utf-8').strip()
                print(line)
        else:
            print("Invalid command")
except KeyboardInterrupt:
    print("Exiting...")
finally:
    ser.close()
