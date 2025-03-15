import asyncio
import serial
import serial.tools.list_ports

class ArduinoController:
    def __init__(self, port=None, baudrate=9600):
        if not port:
            port = self.find_arduino_port() 

        try:
            self.arduino = serial.Serial(port, baudrate, timeout=1)
            print(f"✅ Conectado a Arduino en {port}")
        except Exception as e:
            print(f"⚠️ No se pudo conectar al Arduino: {e}")
            self.arduino = None

    def find_arduino_port(self):
        """Busca el puerto donde está conectado el Arduino automáticamente."""
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if "Arduino" in port.description or "usbmodem" in port.device:
                return port.device
        return "/dev/cu.usbmodem1201"

    async def send_message(self, message):
        if self.arduino:
            self.arduino.write((message + "\n").encode()) 
        else:
            print("⚠️ Arduino no está conectado.")

    async def authorize_access(self):
        print("🟢 LED VERDE ENCENDIDO")
        await self.send_message('A')
        asyncio.create_task(self.turnoff_leds_after_delay(5))

    async def unauthorize_access(self):
        print("🔴 LED ROJO ENCENDIDO")
        await self.send_message('D')
        asyncio.create_task(self.turnoff_leds_after_delay(5))

    async def turnoff_leds_after_delay(self, delay):
        await asyncio.sleep(delay)
        print("⚫ Apagando LEDs...")
        await self.send_message('O')

    async def send_display_message(self, text):
        """Envía un mensaje al LCD del Arduino."""
        if len(text) > 50:
            print("⚠️ El mensaje es demasiado largo (máx 50 caracteres).")
            return
        print(f"📟 Mostrando en LCD: {text}")
        await self.send_message(f"M:{text}")

