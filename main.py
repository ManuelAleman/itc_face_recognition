import asyncio
from config.db import db
from access_control_area.add_user import add_new_user, add_users_from_dataset
from access_control_area.verify_access import start_camera

async def main():
    await db.connect()
    
    #await add_new_user()
    #await verify_access_camera()
    #await add_users_from_dataset()

    
    await start_camera()

    await db.disconnect()

if __name__ == "__main__":
    asyncio.run(main())

