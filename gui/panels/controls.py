import customtkinter as ctk
from core.auth import load_config, save_config

class ControlsPanel(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.start_callback = None
        self.stop_callback = None
        
        # Logo
        lbl_logo = ctk.CTkLabel(self, text="SimSlayer", font=("Segoe UI Bold", 24), text_color="#2563EB")
        lbl_logo.pack(pady=(10, 0))
        lbl_sub = ctk.CTkLabel(self, text="Simcluster Tournament Bot", font=("Segoe UI", 12), text_color="#6B7280")
        lbl_sub.pack(pady=(0, 10))
        
        ctk.CTkFrame(self, height=1, fg_color="#E5E7EB").pack(fill="x", padx=10, pady=5)
        
        # API Configuration
        lbl_api = ctk.CTkLabel(self, text="API Configuration", font=("Segoe UI Bold", 14), text_color="#111827")
        lbl_api.pack(anchor="w", padx=10, pady=(5, 5))
        
        self.entries = {}
        for field in ["api_key", "api_secret", "bearer_token", "access_token", "access_token_secret"]:
            lbl = ctk.CTkLabel(self, text=field.replace("_", " ").title(), font=("Segoe UI", 10), text_color="#6B7280")
            lbl.pack(anchor="w", padx=10)
            entry = ctk.CTkEntry(self, show="*", height=28)
            entry.pack(fill="x", padx=10, pady=(0, 5))
            self.entries[field] = entry
            
        self.show_keys_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(self, text="Show Keys", variable=self.show_keys_var, font=("Segoe UI", 11), command=self.toggle_keys).pack(anchor="w", padx=10, pady=5)

        lbl_warn1 = ctk.CTkLabel(self, text="⚠ Basic API plan required ($100/mo)", font=("Segoe UI", 10), text_color="#D97706")
        lbl_warn1.pack(anchor="w", padx=10)

        btn_save = ctk.CTkButton(self, text="Save Keys", fg_color="transparent", border_color="#2563EB", border_width=1, text_color="#2563EB", hover_color="#eff6ff", command=self.save_keys)
        btn_save.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkFrame(self, height=1, fg_color="#E5E7EB").pack(fill="x", padx=10, pady=5)

        # Targeting
        lbl_target = ctk.CTkLabel(self, text="Targeting", font=("Segoe UI Bold", 14), text_color="#111827")
        lbl_target.pack(anchor="w", padx=10, pady=(5, 5))
        
        ctk.CTkLabel(self, text="Keywords", font=("Segoe UI", 10), text_color="#6B7280").pack(anchor="w", padx=10)
        self.entry_kw = ctk.CTkEntry(self, placeholder_text="AI, ChatGPT, Claude, assistant")
        self.entry_kw.pack(fill="x", padx=10, pady=(0, 5))
        self.entry_kw.insert(0, "AI, ChatGPT, Claude, assistant")

        self.slider_interval = ctk.CTkSlider(self, from_=60, to=300, number_of_steps=24, command=self.update_interval_lbl)
        self.slider_interval.pack(fill="x", padx=10, pady=(10,0))
        self.lbl_interval = ctk.CTkLabel(self, text="60s — safe minimum", font=("Segoe UI", 10), text_color="#6B7280")
        self.lbl_interval.pack(anchor="w", padx=10, pady=(0, 5))
        self.slider_interval.set(60)
        
        self.slider_maxrep = ctk.CTkSlider(self, from_=1, to=20, number_of_steps=19, command=self.update_maxrep_lbl)
        self.slider_maxrep.pack(fill="x", padx=10, pady=(10,0))
        self.lbl_maxrep = ctk.CTkLabel(self, text="Keep low to avoid suspension (12)", font=("Segoe UI", 10), text_color="#6B7280")
        self.lbl_maxrep.pack(anchor="w", padx=10, pady=(0, 5))
        self.slider_maxrep.set(12)

        self.var_verified = ctk.BooleanVar(value=False)
        ctk.CTkSwitch(self, text="Verified bots only", variable=self.var_verified, font=("Segoe UI", 12)).pack(anchor="w", padx=10, pady=5)
        
        self.var_threads = ctk.BooleanVar(value=True)
        ctk.CTkSwitch(self, text="Threads only", variable=self.var_threads, font=("Segoe UI", 12)).pack(anchor="w", padx=10, pady=5)
        
        ctk.CTkLabel(self, text="⚠ Use a throwaway account, not your main", font=("Segoe UI", 10), text_color="#D97706").pack(anchor="w", padx=10, pady=5)

        ctk.CTkFrame(self, height=1, fg_color="#E5E7EB").pack(fill="x", padx=10, pady=5)

        # Controls
        lbl_ctrl = ctk.CTkLabel(self, text="Controls", font=("Segoe UI Bold", 14), text_color="#111827")
        lbl_ctrl.pack(anchor="w", padx=10, pady=(5, 5))
        
        self.btn_start = ctk.CTkButton(self, text="▶ Start", fg_color="#2563EB", hover_color="#1d4ed8", font=("Segoe UI Bold", 14), command=self.click_start)
        self.btn_start.pack(fill="x", padx=10, pady=5)
        
        self.btn_stop = ctk.CTkButton(self, text="■ Stop", fg_color="#DC2626", hover_color="#b91c1c", font=("Segoe UI Bold", 14), command=self.click_stop, state="disabled")
        self.btn_stop.pack(fill="x", padx=10, pady=5)

        self.lbl_status = ctk.CTkLabel(self, text=" IDLE ", fg_color="#E5E7EB", text_color="#6B7280", font=("Segoe UI Bold", 12), corner_radius=10)
        self.lbl_status.pack(pady=10)
        
        self.load_keys()

    def update_interval_lbl(self, val):
        self.lbl_interval.configure(text=f"{int(val)}s — {('safe minimum' if val <= 60 else 'interval')}")
        
    def update_maxrep_lbl(self, val):
        self.lbl_maxrep.configure(text=f"Keep low to avoid suspension ({int(val)})")

    def toggle_keys(self):
        show = "" if self.show_keys_var.get() else "*"
        for e in self.entries.values():
            e.configure(show=show)

    def load_keys(self):
        cfg = load_config()
        for k, e in self.entries.items():
            if k in cfg:
                e.delete(0, 'end')
                e.insert(0, cfg[k])

    def save_keys(self):
        cfg = load_config()
        for k, e in self.entries.items():
            cfg[k] = e.get()
        save_config(cfg)
        self.lbl_status.configure(text=" KEYS SAVED ", fg_color="#16A34A", text_color="white")
        self.after(2000, self.reset_status)

    def reset_status(self):
        if self.btn_start.cget("state") == "normal":
            self.lbl_status.configure(text=" IDLE ", fg_color="#E5E7EB", text_color="#6B7280")
        else:
            self.lbl_status.configure(text=" RUNNING ", fg_color="#16A34A", text_color="white")

    def click_start(self):
        if self.start_callback:
            config_vars = {
                "keywords": self.entry_kw.get(),
                "interval": self.slider_interval.get(),
                "max_replies": self.slider_maxrep.get(),
                "verified_only": self.var_verified.get(),
                "threads_only": self.var_threads.get()
            }
            self.start_callback(config_vars)
            self.btn_start.configure(state="disabled")
            self.btn_stop.configure(state="normal")
            self.lbl_status.configure(text=" RUNNING ", fg_color="#16A34A", text_color="white")
            for e in self.entries.values():
                e.configure(state="disabled")

    def click_stop(self):
        if self.stop_callback:
            self.stop_callback()
            self.btn_start.configure(state="normal")
            self.btn_stop.configure(state="disabled")
            self.lbl_status.configure(text=" STOPPED ", fg_color="#DC2626", text_color="white")
            for e in self.entries.values():
                e.configure(state="normal")

    def set_start_callback(self, cb):
        self.start_callback = cb
        
    def set_stop_callback(self, cb):
        self.stop_callback = cb
