import serial
import time
import csv
import datetime
import os

# Set up the serial connection (adjust '/dev/cu.usbserial-120' to your specific port)
ser = serial.Serial('/dev/cu.usbserial-10', 9600, timeout=1)

# Give the connection a second to settle
time.sleep(2)

# Function to prompt user for metadata
def get_user_defined_metadata():
    metadata = {
        "Arduino ID": input("Enter Arduino ID: "),
        "Sensor ID": input("Enter Sensor ID: "),
        "Range (cm)": input("Enter Range (cm): "),
        "Sensor length (cm)": input("Enter Sensor length (cm): "),
        "Color of sensor": input("Enter Color of sensor: "),
        "Angle on XY plane": input("Enter Angle on XY plane: "),
        "side a (cm)": input("Enter side a (cm): "),
        "side b (cm)": input("Enter side b (cm): "),
        "side c (cm)": input("Enter side c (cm): "),
        "Angle on YZ plane": input("Enter Angle on YZ plane: "),
        "Sensor Configuration": input("Enter Sensor Configuration: "),
        "Sensor Angle": input("Enter Sensor Angle: "),
        "Surface material": input("Enter Surface material: "),
        "Surface Length (cm)": input("Enter Surface Length (cm): "),
        "Surface Width (cm)": input("Enter Surface Width (cm): "),

    }
    return metadata

# Function to automatically generate filename for sequence recording
def generate_sequence_filename(metadata):
    current_date = datetime.datetime.now().strftime("%H_%M_%S_%d%m%Y")
    return f"ultra_sonic_sensor/fully_automate/data_v4/test_seq_ard{metadata['Arduino ID']}_sensor{metadata['Sensor ID']}_{current_date}.csv"

def generate_delay_sequence_filename(metadata):
    current_date = datetime.datetime.now().strftime("%H_%M_%S_%d%m%Y")
    return f"ultra_sonic_sensor/fully_automate/data_v4/test_delay_seq_ard{metadata['Arduino ID']}_sensor{metadata['Sensor ID']}_range{metadata['Range (cm)']}_{current_date}.csv"

# Function to record data
def record_data(metadata, output_file):
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = [
            'Trial', 'Ping Duration', 'Distance (cm)', 'Ping Time (us)', 'Delay (us)','Steps',
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
                if line == "Sample collection complete.":
                    time.sleep(3)
                data = line.split(',')
                if len(data) == 7:  # Ensure we have all the parts of the data
                    row = {
                        'Trial': data[0],
                        'Ping Duration': data[1],
                        'Distance (cm)': data[2],
                        'Ping Time (us)': data[3],
                        'Steps': data[5],
                        'Delay (us)': data[6],
                    }
                    row.update(metadata)
                    writer.writerow(row)
            else:
                break
            

# Function to send commands to the Arduino
def send_command(command):
    ser.write((command + '\n').encode())
    time.sleep(1)  # Wait for a second to ensure the command is processed


# Function to send rotation command to the Arduino
def rotate_stepper():
    command = input("Enter direction (ex. 'F0.5' for forward rotation and 'R1.5' for reverse rotation): ").strip().upper()
    send_command(command)
    print(f"Rotation command '{command}' sent.")

try:
    print(f"\n==================={os.path.basename(__file__)}===================")
    print("CAUTION: For Millisecond delay try not to go over 20ms data may not recorded.")
    print("CAUTION: Microsecond max is 16800.")
    while True:
        lines = ser.readlines()
        for line in lines:
            print("\t>>> "+line.decode('utf-8').strip())

        user_input = input("Enter 'M' to set delay in milliseconds, 'U' to set delay in microseconds, 'S' to run sequence, 'T' to rotate stepper motor, 'reset' to reset stepper motor, or 'q' to quit: ")
        if user_input.lower() == 'q':
            break
        elif user_input in ['M', 'U', 'S', 'T','P', 'reset']:
            send_command(user_input)
            if user_input in ['M', 'U']:
                delay_value = input(f"Enter the delay value in {'milliseconds' if user_input == 'M' else 'microseconds'}: ")
                send_command(f"D{delay_value}")
                lines = ser.readlines()
                for line in lines:
                    print("\t>>> "+line.decode('utf-8').strip())
            elif user_input.lower() == 's':
                metadata = get_user_defined_metadata()
                filename = generate_sequence_filename(metadata)
                send_command("run")
                record_data(metadata, filename)
                print("Motor Sequence complete. Data recorded.")
            elif user_input.lower() == 'p':
                metadata = get_user_defined_metadata()
                filename = generate_delay_sequence_filename(metadata)
                #send_command("p")
                record_data(metadata, filename)
                print("Delay Sequence complete. Data recorded.")
            elif user_input.lower() == 't':
                rotate_stepper()
                lines = ser.readlines()
                for line in lines:
                    print("\t>>> "+line.decode('utf-8').strip())
            elif user_input.lower() == 'reset':
                send_command("reset")
                lines = ser.readlines()
                for line in lines:
                    print("\t>>> "+line.decode('utf-8').strip())
                print("Stepper motor reset.")
        else:
            print("Invalid command")
except KeyboardInterrupt:
    print("Exiting...")
finally:
    ser.close()
