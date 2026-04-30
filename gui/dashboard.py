import customtkinter as ctk
import os
from .panels.controls import ControlsPanel
from .panels.livefeed import LiveFeedPanel
from .panels.stats import StatsPanel
from .panels.payload_editor import PayloadEditorPanel

ctk.set_appearance_mode("Light")

class SimSlayerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SimSlayer — Simcluster Tournament Bot")
        self.geometry("1200x750")
        self.configure(fg_color="#F5F5F5")
        
        self.grid_columnconfigure(0, weight=0, minsize=280)
        self.grid_columnconfigure(1, weight=1)             
        self.grid_columnconfigure(2, weight=0, minsize=220)
        self.grid_rowconfigure(0, weight=1)                 
        self.grid_rowconfigure(1, weight=0)                 

        from core.bot import SimSlayerBot
        self.bot = SimSlayerBot(self.push_to_feed, self.update_stats)

        self.panels = {}
        
        self.panels['controls'] = ControlsPanel(self, corner_radius=12, fg_color="#FFFFFF", border_color="#E5E7EB", border_width=1)
        self.panels['controls'].grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.panels['livefeed'] = LiveFeedPanel(self, corner_radius=12, fg_color="#FFFFFF", border_color="#E5E7EB", border_width=1)
        self.panels['livefeed'].grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        self.panels['stats'] = StatsPanel(self, corner_radius=12, fg_color="#FFFFFF", border_color="#E5E7EB", border_width=1)
        self.panels['stats'].grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        
        self.panels['payloads'] = PayloadEditorPanel(self, corner_radius=12, fg_color="#FFFFFF", border_color="#E5E7EB", border_width=1)
        self.panels['payloads'].grid(row=1, column=0, columnspan=3, padx=10, pady=(0,10), sticky="nsew")
        self.panels['payloads'].grid_remove() # hide by default until toggled
        
        self.panels['controls'].set_start_callback(self.start_bot)
        self.panels['controls'].set_stop_callback(self.stop_bot)
        self.panels['stats'].set_toggle_drawer_callback(self.toggle_payload_drawer)
        
        self.after(500, self.check_initial_warning)

    def toggle_payload_drawer(self):
        if self.panels['payloads'].winfo_viewable():
            self.panels['payloads'].grid_remove()
        else:
            self.panels['payloads'].grid()
            self.panels['payloads'].load_payloads()

    def check_initial_warning(self):
        from core.auth import load_config
        config = load_config()
        if config.get("show_warning", True):
            self.show_startup_modal()

    def show_startup_modal(self):
        dialog = StartupModal(self)
        self.wait_window(dialog)

    def start_bot(self, config_vars):
        self.bot.start(config_vars)
        
    def stop_bot(self):
        self.bot.stop()

    def push_to_feed(self, badge, msg):
        self.after(0, lambda: self.panels['livefeed'].add_log(badge, msg))
        
    def update_stats(self):
        self.after(0, lambda: self.panels['stats'].refresh_stats())


class StartupModal(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("⚠ Before You Start — Read This")
        self.geometry("450x450")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", lambda: None)
        self.transient(self.master)
        self.grab_set()

        content = (
            "┌─────────────────────────────────────────┐\n"
            "│  ⚠  Important Warnings                 │\n"
            "│─────────────────────────────────────────│\n"
            "│                                         │\n"
            "│  🐦 X API Limits                        │\n"
            "│  The free API tier allows only ~17      │\n"
            "│  tweets/day. You need the Basic plan    │\n"
            "│  ($100/mo) minimum to be competitive.  │\n"
            "│                                         │\n"
            "│  🔒 Account Safety                      │\n"
            "│  Use a throwaway X account — NOT your  │\n"
            "│  main. X may suspend automated          │\n"
            "│  accounts. Keep reply intervals 60s+.  │\n"
            "│                                         │\n"
            "│  📋 Competition Rules                   │\n"
            "│  Verify the full Simcluster rules       │\n"
            "│  before running. Confirm: entry         │\n"
            "│  requirements, scoring method,          │\n"
            "│  and submission deadline.               │\n"
            "│                                         │\n"
            "│  ⚡ Best Strategy                       │\n"
            "│  Start slow. Let the success tracker    │\n"
            "│  identify which payloads work before   │\n"
            "│  ramping up volume.                     │\n"
            "└─────────────────────────────────────────┘\n"
        )
        
        lbl = ctk.CTkLabel(self, text=content, justify="left", font=("Consolas", 12), text_color="#111827")
        lbl.pack(padx=20, pady=20)
        
        self.dont_show_var = ctk.BooleanVar(value=False)
        chk = ctk.CTkCheckBox(self, text="Don't show again", variable=self.dont_show_var, font=("Segoe UI", 12))
        chk.pack(pady=5)
        
        btn = ctk.CTkButton(self, text="I understand, let's go", fg_color="#2563EB", text_color="#FFFFFF", font=("Segoe UI Bold", 13), command=self.close)
        btn.pack(pady=10)

    def close(self):
        if self.dont_show_var.get():
            from core.auth import load_config, save_config
            cfg = load_config()
            cfg["show_warning"] = False
            save_config(cfg)
        self.grab_release()
        self.destroy()
