import asyncio
from config.db import db
from access_control_area.add_user import add_new_user, add_users_from_dataset

async def main():
    await db.connect()
    
    #await add_new_user()
    await add_users_from_dataset()

    await db.disconnect()

if __name__ == "__main__":
    asyncio.run(main())

