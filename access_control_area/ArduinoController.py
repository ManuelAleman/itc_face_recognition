import serial
import time

class ArduinoController:
    def __init__(self, port="/dev/ttyACM0", baudrate=9600):
        try:
            self.arduino = serial.Serial(port, baudrate, timeout=1)
            time.sleep(2)
        except Exception as e:
            print(f"⚠️ Unable to connect to Arduino: {e}")
            self.arduino = None

    def send_message(self, message):
        if self.arduino:
            self.arduino.write(message.encode())
            time.sleep(1)
        else:
            print("⚠️ Arduino is not connected.")

    def authorize_access(self):
        print(f"GREEN LED ON")
        self.send_message('A')

    def unauthorize_access(self):
        print(f"RED LED ON")
        self.send_message('D')

    def turnoff_leds(self):
        print(f"TURNING OFF LEDS")
        self.send_message('O')