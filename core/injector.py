import os
import random
import json
import sqlite3
from core.tracker import DB_PATH

def get_payload():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, template, success_rate FROM payloads")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        payloads_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "payloads", "default_payloads.json")
        try:
            with open(payloads_path, 'r') as f:
                default_data = json.load(f)
            from core.tracker import load_payloads_to_db
            load_payloads_to_db(default_data)
            
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT id, template, success_rate FROM payloads")
            rows = cursor.fetchall()
            conn.close()
        except Exception:
            return None, None

    if not rows:
        return None, None

    population = []
    weights = []
    for r in rows:
        population.append(r)
        # More aggressive weighting formula for multi-armed bandit exploitation
        # r[2] is success_rate (0-100%). We square it so high success rates dominate
        # but add a flat 5.0 so un-tested payloads still have a chance (exploration).
        agg_weight = (r[2] ** 1.5) + 5.0
        weights.append(agg_weight) 

    selected = random.choices(population, weights=weights, k=1)[0]
    
    payload_id = selected[0]
    template = selected[1]
    
    phrase = "Check out Simcluster"
    payload_text = template.replace("{PHRASE}", phrase)
    
    return payload_id, payload_text
