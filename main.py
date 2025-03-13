from views.FaceRecognitionApp import FaceRecognitionApp
from views.AdminPanel import AdminPanel
import tkinter as tk
import sys
import asyncio
from config.db import db
def main():
    if len(sys.argv) > 1 and sys.argv[1] == "admin":
        loop = asyncio.get_event_loop()
        loop.run_until_complete(db.connect())
        
        app = AdminPanel()
        app.mainloop()

        loop.run_until_complete(db.disconnect())
        sys.exit(1)
    else:
        root = tk.Tk()
        app = FaceRecognitionApp(root)
        root.mainloop()
        
if __name__ == "__main__":
    main()
