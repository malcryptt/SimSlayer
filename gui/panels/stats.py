import customtkinter as ctk
import time
from core.tracker import get_stats, get_top_payloads, get_warning_count_today

class StatsPanel(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.toggle_cb = None
        
        ctk.CTkLabel(self, text="Session Stats", font=("Segoe UI Bold", 16), text_color="#111827").pack(pady=(15, 10))
        
        # Stat cards
        self.lbl_sent = self._create_stat_card("📤 Tweets Sent", "0")
        self.lbl_targeted = self._create_stat_card("🎯 Bots Targeted", "0")
        self.lbl_hits = self._create_stat_card("✅ Hits", "0", val_color="#16A34A")
        self.lbl_misses = self._create_stat_card("❌ Misses", "0", val_color="#DC2626")
        self.lbl_warnings = self._create_stat_card("⚠ API Warnings", "0", val_color="#D97706")
        
        # Hit Rate
        self.hit_rate_lbl = ctk.CTkLabel(self, text="0% Hit Rate", font=("Segoe UI Bold", 12), text_color="#2563EB")
        self.hit_rate_lbl.pack(anchor="w", padx=15, pady=(10, 0))
        self.progressbar = ctk.CTkProgressBar(self, height=8, fg_color="#E5E7EB", progress_color="#2563EB")
        self.progressbar.pack(fill="x", padx=15, pady=5)
        self.progressbar.set(0)
        
        # Timer
        self.start_time = time.time()
        self.lbl_timer = ctk.CTkLabel(self, text="Session: 00:00:00", font=("Segoe UI", 12), text_color="#6B7280")
        self.lbl_timer.pack(pady=5)
        self.update_timer()
        
        ctk.CTkFrame(self, height=1, fg_color="#E5E7EB").pack(fill="x", padx=10, pady=10)
        
        # Top Payloads
        ctk.CTkLabel(self, text="Top Payloads", font=("Segoe UI Bold", 14), text_color="#111827").pack(anchor="w", padx=15)
        self.payload_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.payload_frame.pack(fill="x", padx=15, pady=5)
        self.payload_rows = []
        for _ in range(3):
            # name | success % | bar
            row = ctk.CTkFrame(self.payload_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)
            name_lbl = ctk.CTkLabel(row, text="-", font=("Segoe UI", 10), text_color="#111827", width=120, anchor="w")
            name_lbl.pack(side="left")
            pct_lbl = ctk.CTkLabel(row, text="0%", font=("Segoe UI Bold", 10), text_color="#2563EB", width=30)
            pct_lbl.pack(side="left")
            self.payload_rows.append((name_lbl, pct_lbl))
            
        ctk.CTkFrame(self, height=1, fg_color="#E5E7EB").pack(fill="x", padx=10, pady=10)
        
        # Account Health
        ctk.CTkLabel(self, text="Account Health", font=("Segoe UI Bold", 14), text_color="#111827").pack(anchor="w", padx=15)
        self.lbl_health_status = ctk.CTkLabel(self, text="🟢 Status: OK", font=("Segoe UI", 12), text_color="#16A34A")
        self.lbl_health_status.pack(anchor="w", padx=15, pady=2)
        
        self.lbl_health_replies = ctk.CTkLabel(self, text="Replies this hour: 0", font=("Segoe UI", 11), text_color="#6B7280")
        self.lbl_health_replies.pack(anchor="w", padx=15, pady=2)

        export_btn = ctk.CTkButton(self, text="📥 Export Results", fg_color="#E5E7EB", text_color="#111827", hover_color="#D1D5DB", command=self.export_results)
        export_btn.pack(fill="x", padx=15, pady=(20,5))
        
        self.btn_toggle = ctk.CTkButton(self, text="✏ Edit Payloads ▾", fg_color="transparent", text_color="#2563EB", hover_color="#eff6ff", command=self.do_toggle)
        self.btn_toggle.pack(fill="x", padx=15, pady=5)
        
    def _create_stat_card(self, title, initial_val, val_color="#111827"):
        card = ctk.CTkFrame(self, fg_color="#F9FAFB", corner_radius=8, border_color="#E5E7EB", border_width=1)
        card.pack(fill="x", padx=15, pady=3)
        ctk.CTkLabel(card, text=title, font=("Segoe UI", 11), text_color="#6B7280").pack(side="left", padx=10, pady=5)
        val_lbl = ctk.CTkLabel(card, text=initial_val, font=("Segoe UI Bold", 14), text_color=val_color)
        val_lbl.pack(side="right", padx=10, pady=5)
        return val_lbl

    def update_timer(self):
        elapsed = int(time.time() - self.start_time)
        hrs = elapsed // 3600
        mins = (elapsed % 3600) // 60
        secs = elapsed % 60
        self.lbl_timer.configure(text=f"Session: {hrs:02d}:{mins:02d}:{secs:02d}")
        self.after(1000, self.update_timer)

    def refresh_stats(self):
        try:
            stats = get_stats()
            self.lbl_sent.configure(text=str(stats["sent"]))
            self.lbl_targeted.configure(text=str(stats["targeted"]))
            self.lbl_hits.configure(text=str(stats["hits"]))
            self.lbl_misses.configure(text=str(stats["misses"]))
            self.lbl_warnings.configure(text=str(stats["warnings"]))
            
            hr = stats["hit_rate"]
            self.hit_rate_lbl.configure(text=f"{hr:.1f}% Hit Rate")
            self.progressbar.set(hr / 100.0)
            
            top = get_top_payloads(3)
            for i in range(3):
                if i < len(top):
                    self.payload_rows[i][0].configure(text=top[i]["name"][:15])
                    self.payload_rows[i][1].configure(text=f"{top[i]['success_rate']:.0f}%")
                else:
                    self.payload_rows[i][0].configure(text="-")
                    self.payload_rows[i][1].configure(text="0%")
                    
            w_today = get_warning_count_today()
            if w_today > 5:
                self.lbl_health_status.configure(text="🔴 Suspension Risk — Slow down", text_color="#DC2626")
            else:
                self.lbl_health_status.configure(text="🟢 Status: OK", text_color="#16A34A")
        except Exception:
            pass

    def do_toggle(self):
        if self.toggle_cb:
            self.toggle_cb()

    def set_toggle_drawer_callback(self, cb):
        self.toggle_cb = cb

    def export_results(self):
        import sqlite3
        from core.tracker import DB_PATH
        import csv
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            with open("results.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "target_account", "bot_score", "payload_used", "hit"])
                cursor.execute("SELECT timestamp, target_account, payload_text, hit FROM shots")
                for row in cursor.fetchall():
                    writer.writerow([row[0], row[1], "?", row[2], row[3]])
            
            with open("results.txt", "w", encoding="utf-8") as f:
                f.write("SimSlayer Session Report\n========================\n")
                stats = get_stats()
                f.write(f"Total Sent:    {stats['sent']}\n")
                f.write(f"Total Hits:    {stats['hits']}\n")
                f.write(f"Hit Rate:      {stats['hit_rate']:.1f}%\n\n")
                
                f.write("HIT LOG:\n")
                cursor.execute("SELECT timestamp, target_account, payload_text FROM shots WHERE hit = 1")
                for h in cursor.fetchall():
                    f.write(f"[{h[0]}] @{h[1]} hit by payload\n")
            conn.close()
        except Exception as e:
            print("Export failed:", e)
