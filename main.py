import asyncio
from config.db import db
from access_control_area.verify_access import verify_access_camera
from access_control_area.add_user import add_new_user

async def main():
    await db.connect()

    #await add_new_user()

    await verify_access_camera()

    # await test_dlib()

    await db.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
