from views.FaceRecognitionApp import FaceRecognitionApp
from views.AdminPanel import AdminPanel
from views.SelectClass import SelectClass
from views.Report import Report
import threading
import sys
import asyncio
from config.db import db
def main():
    asyncio.set_event_loop(asyncio.new_event_loop())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(db.connect())
    if len(sys.argv) > 1 and sys.argv[1] == "admin":
        app = AdminPanel()
    elif len(sys.argv) > 1 and sys.argv[1] == "report":
        app = Report()
    else:
        app = SelectClass()
    app.mainloop()
    loop.run_until_complete(db.disconnect())
        
if __name__ == "__main__":
    main()
