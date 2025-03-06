import asyncio
from config.db import db
from models.access import create_access
from verify_access import verify_access_camera
from add_user import add_new_user
async def main():
    await db.connect()
    
    await add_new_user()
    #await verify_access_camera()

    await db.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
