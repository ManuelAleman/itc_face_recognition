import asyncio
import serial

class ArduinoController:
    def __init__(self, port="/dev/cu.usbmodem1201", baudrate=9600):
        try:
            self.arduino = serial.Serial(port, baudrate, timeout=1)
        except Exception as e:
            print(f"⚠️ Unable to connect to Arduino: {e}")
            self.arduino = None

    def initialize(self):
        print("Arduino initialized")

    async def send_message(self, message):
        if self.arduino:
            self.arduino.write(message.encode())
        else:
            print("⚠️ Arduino is not connected.")

    async def authorize_access(self):
        print("GREEN LED ON")
        await self.send_message('A')
        asyncio.create_task(self.turnoff_leds_after_delay(5))

    async def unauthorize_access(self):
        print("RED LED ON")
        await self.send_message('D')
        asyncio.create_task(self.turnoff_leds_after_delay(5))

    async def turnoff_leds_after_delay(self, delay):
        await asyncio.sleep(delay)
        print("TURNING OFF LEDS")
        await self.send_message('O')

    async def send_display_message(self, text):
        """Envía un mensaje para que se muestre en la pantalla LED del Arduino."""
        if len(text) > 50:
            print("⚠️ El mensaje es demasiado largo (máx 50 caracteres).")
            return
        await self.send_message(f"M:{text}")
        
