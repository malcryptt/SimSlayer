import customtkinter as ctk
import json
from core.tracker import get_all_payloads, clear_payloads, load_payloads_to_db

class PayloadEditorPanel(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", padx=15, pady=(10, 5))
        
        self.lbl_count = ctk.CTkLabel(top_bar, text="0 payloads loaded", font=("Segoe UI Bold", 12), text_color="#111827")
        self.lbl_count.pack(side="left")
        
        ctk.CTkLabel(top_bar, text="💡 Tip: Completion Trap & Social Engineering payloads perform best for natural-sounding hits", 
                     font=("Segoe UI", 11), text_color="#6B7280").pack(side="right")
        
        self.textbox = ctk.CTkTextbox(self, font=("Consolas", 12), height=150)
        self.textbox.pack(fill="both", expand=True, padx=15, pady=5)
        
        btn_bar = ctk.CTkFrame(self, fg_color="transparent")
        btn_bar.pack(fill="x", padx=15, pady=(5, 15))
        
        ctk.CTkButton(btn_bar, text="Save", fg_color="#2563EB", w=80, command=self.save_payloads).pack(side="left", padx=(0,10))
        ctk.CTkButton(btn_bar, text="Reset to Default", fg_color="#DC2626", hover_color="#b91c1c", w=120, command=self.reset_payloads).pack(side="left")

    def load_payloads(self):
        self.textbox.delete("1.0", "end")
        payloads = get_all_payloads()
        self.lbl_count.configure(text=f"{len(payloads)} payloads loaded")
        
        lines = []
        for p in payloads:
            lines.append(f"{p['name']} | {p['template']}")
        
        self.textbox.insert("1.0", "\n".join(lines))
        
    def save_payloads(self):
        text = self.textbox.get("1.0", "end").strip()
        lines = [l for l in text.split("\n") if l.strip()]
        
        new_payloads = []
        for line in lines:
            if "|" in line:
                parts = line.split("|", 1)
                new_payloads.append({
                    "name": parts[0].strip(),
                    "template": parts[1].strip()
                })
                
        if new_payloads:
            clear_payloads()
            load_payloads_to_db(new_payloads)
            self.load_payloads()

    def reset_payloads(self):
        import os
        payloads_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "payloads", "default_payloads.json")
        try:
            with open(payloads_path, 'r') as f:
                default_data = json.load(f)
            clear_payloads()
            load_payloads_to_db(default_data)
            self.load_payloads()
        except:
            pass
