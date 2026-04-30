import sqlite3
import os
import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "simslayer.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shots (
            id INTEGER PRIMARY KEY,
            timestamp TEXT,
            target_account TEXT,
            target_tweet_id TEXT,
            payload_id INTEGER,
            payload_text TEXT,
            our_reply_id TEXT,
            hit INTEGER DEFAULT 0,
            checked INTEGER DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payloads (
            id INTEGER PRIMARY KEY,
            name TEXT,
            template TEXT,
            times_used INTEGER DEFAULT 0,
            times_hit INTEGER DEFAULT 0,
            success_rate REAL DEFAULT 0.0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS warnings (
            id INTEGER PRIMARY KEY,
            timestamp TEXT,
            type TEXT,
            message TEXT
        )
    """)
    conn.commit()
    conn.close()

def log_shot(target_account, target_tweet_id, payload_id, payload_text, our_reply_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO shots (timestamp, target_account, target_tweet_id, payload_id, payload_text, our_reply_id, hit)
        VALUES (?, ?, ?, ?, ?, ?, 0)
    """, (now_str, target_account, target_tweet_id, payload_id, payload_text, our_reply_id))
    
    cursor.execute("""
        UPDATE payloads 
        SET times_used = times_used + 1 
        WHERE id = ?
    """, (payload_id,))
    
    calculate_success_rate(cursor, payload_id)
    
    conn.commit()
    conn.close()

def mark_hit(our_reply_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE shots SET hit = 1, checked = 1 WHERE our_reply_id = ?", (our_reply_id,))
    
    cursor.execute("SELECT payload_id FROM shots WHERE our_reply_id = ?", (our_reply_id,))
    row = cursor.fetchone()
    if row:
        payload_id = row[0]
        cursor.execute("UPDATE payloads SET times_hit = times_hit + 1 WHERE id = ?", (payload_id,))
        calculate_success_rate(cursor, payload_id)
    
    conn.commit()
    conn.close()

def calculate_success_rate(cursor, payload_id):
    cursor.execute("SELECT times_used, times_hit FROM payloads WHERE id = ?", (payload_id,))
    row = cursor.fetchone()
    if row:
        used, hit = row[0], row[1]
        success_rate = (hit / used) * 100 if used > 0 else 0.0
        cursor.execute("UPDATE payloads SET success_rate = ? WHERE id = ?", (success_rate, payload_id))

def get_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM shots")
    sent = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(DISTINCT target_account) FROM shots")
    targeted = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM shots WHERE hit = 1")
    hits = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM shots WHERE hit = 0")
    misses = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM warnings")
    warnings_count = cursor.fetchone()[0]
    conn.close()
    
    hit_rate = (hits / sent * 100) if sent > 0 else 0
    return {
        "sent": sent,
        "targeted": targeted,
        "hits": hits,
        "misses": misses,
        "warnings": warnings_count,
        "hit_rate": hit_rate
    }

def get_top_payloads(n=3):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name, success_rate FROM payloads ORDER BY success_rate DESC, times_used DESC LIMIT ?", (n,))
    rows = cursor.fetchall()
    conn.close()
    return [{"name": r[0], "success_rate": r[1]} for r in rows]

def already_targeted(tweet_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM shots WHERE target_tweet_id = ?", (tweet_id,))
    row = cursor.fetchone()
    conn.close()
    return row is not None

def log_warning(warning_type, message):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO warnings (timestamp, type, message) VALUES (?, ?, ?)", (now_str, warning_type, message))
    conn.commit()
    conn.close()

def get_warning_count_today():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        today_prefix = datetime.datetime.now().strftime("%Y-%m-%d") + "%"
        cursor.execute("SELECT COUNT(*) FROM warnings WHERE timestamp LIKE ?", (today_prefix,))
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception:
        return 0

def load_payloads_to_db(payloads_list):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    for p in payloads_list:
        cursor.execute("SELECT 1 FROM payloads WHERE name = ?", (p['name'],))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO payloads (name, template) VALUES (?, ?)", (p['name'], p['template']))
    conn.commit()
    conn.close()
    
def get_all_payloads():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, template, times_used, times_hit, success_rate FROM payloads")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "template": r[2], "times_used": r[3], "times_hit": r[4], "success_rate": r[5]} for r in rows]

def clear_payloads():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM payloads")
    conn.commit()
    conn.close()
