import customtkinter as ctk
import datetime

class LiveFeedPanel(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(top_frame, text="Live Feed", font=("Segoe UI Bold", 16), text_color="#111827").pack(side="left")
        ctk.CTkButton(top_frame, text="Clear", width=60, height=24, fg_color="#E5E7EB", text_color="#111827", hover_color="#D1D5DB", command=self.clear_feed).pack(side="right")
        
        ctk.CTkFrame(self, height=1, fg_color="#E5E7EB").pack(fill="x", padx=10)
        
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.row_count = 0
        
    def clear_feed(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        self.row_count = 0

    def add_log(self, badge, message):
        row_color = "#FFFFFF" if self.row_count % 2 == 0 else "#F9FAFB"
        self.row_count += 1
        
        row_frame = ctk.CTkFrame(self.scroll_frame, fg_color=row_color, corner_radius=0)
        row_frame.pack(fill="x", pady=1)
        
        time_str = datetime.datetime.now().strftime("[%H:%M:%S]")
        ctk.CTkLabel(row_frame, text=time_str, font=("Consolas", 11), text_color="#9CA3AF").pack(side="left", padx=(10, 5), pady=4)
        
        badge_colors = {
            "SCAN": ("#F3F4F6", "#6B7280"),
            "TARGET": ("#FEF3C7", "#D97706"),
            "SENT": ("#DBEAFE", "#2563EB"),
            "HIT ✓": ("#DCFCE7", "#16A34A"),
            "MISS": ("#FEE2E2", "#DC2626"),
            "WARN ⚠": ("#FFEDD5", "#EA580C")
        }
        
        bg_col, txt_col = badge_colors.get(badge, ("#E5E7EB", "#111827"))
        
        badge_lbl = ctk.CTkLabel(row_frame, text=f" {badge} ", font=("Segoe UI Bold", 10), 
                                 fg_color=bg_col, text_color=txt_col, corner_radius=6)
        badge_lbl.pack(side="left", padx=5, pady=4)
        
        msg_lbl = ctk.CTkLabel(row_frame, text=message, font=("Consolas", 11), text_color="#111827", justify="left")
        msg_lbl.pack(side="left", padx=5, pady=4, fill="x", expand=True)
        
        self.scroll_frame._parent_canvas.yview_moveto(1.0)
