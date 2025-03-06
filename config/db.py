from dotenv import load_dotenv
from prisma import Client

class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._client = Client()
        return cls._instance

    async def connect(self):
        if not self._client.is_connected():
            await self._client.connect()
            print("✅ Conectado a la base de datos")

    async def disconnect(self):
        if self._client.is_connected():
            await self._client.disconnect()
            print("❌ Desconectado de la base de datos")

    def get_client(self):
        return self._client

load_dotenv()

db = Database()
