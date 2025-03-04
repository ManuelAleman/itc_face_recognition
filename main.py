import asyncio
from config.db import db

async def main():
    await db.connect()

    client = db.get_client()
    users = await client.user.find_many()
    print(users)

    await db.disconnect()

asyncio.run(main())