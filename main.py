import customtkinter as ctk
import os
from core.tracker import init_db, DB_PATH
from gui.dashboard import SimSlayerApp

def main():
    if not os.path.exists(DB_PATH):
        init_db()
    
    app = SimSlayerApp()
    app.mainloop()

if __name__ == "__main__":
    main()
