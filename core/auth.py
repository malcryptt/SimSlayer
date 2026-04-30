import os
import json
import uuid
import tweepy
from cryptography.fernet import Fernet

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")

def _get_machine_key():
    machine_id = str(uuid.getnode())
    import base64
    import hashlib
    h = hashlib.sha256(machine_id.encode()).digest()
    return base64.urlsafe_b64encode(h)

def load_config():
    if not os.path.exists(CONFIG_PATH):
        return {
            "api_key": "",
            "api_secret": "",
            "bearer_token": "",
            "access_token": "",
            "access_token_secret": "",
            "show_warning": True
        }
    try:
        with open(CONFIG_PATH, "r") as f:
            data = json.load(f)
    except:
        data = {}
        
    f_obj = Fernet(_get_machine_key())
    
    def decrypt_val(val):
        if not val:
            return ""
        try:
            return f_obj.decrypt(val.encode()).decode()
        except:
            return ""

    return {
        "api_key": decrypt_val(data.get("api_key", "")),
        "api_secret": decrypt_val(data.get("api_secret", "")),
        "bearer_token": decrypt_val(data.get("bearer_token", "")),
        "access_token": decrypt_val(data.get("access_token", "")),
        "access_token_secret": decrypt_val(data.get("access_token_secret", "")),
        "show_warning": data.get("show_warning", True)
    }

def save_config(config_data):
    f_obj = Fernet(_get_machine_key())
    
    def encrypt_val(val):
        if not val:
            return ""
        return f_obj.encrypt(val.encode()).decode()

    encrypted_data = {
        "api_key": encrypt_val(config_data.get("api_key", "")),
        "api_secret": encrypt_val(config_data.get("api_secret", "")),
        "bearer_token": encrypt_val(config_data.get("bearer_token", "")),
        "access_token": encrypt_val(config_data.get("access_token", "")),
        "access_token_secret": encrypt_val(config_data.get("access_token_secret", "")),
        "show_warning": config_data.get("show_warning", True)
    }
    
    with open(CONFIG_PATH, "w") as f:
        json.dump(encrypted_data, f, indent=4)

def get_tweepy_client():
    config = load_config()
    
    if not all([config.get("api_key"), config.get("api_secret"), config.get("access_token"), config.get("access_token_secret")]):
        raise ValueError("Missing API keys in configuration.")
    
    client = tweepy.Client(
        bearer_token=config.get("bearer_token") or None,
        consumer_key=config.get("api_key"),
        consumer_secret=config.get("api_secret"),
        access_token=config.get("access_token"),
        access_token_secret=config.get("access_token_secret"),
        wait_on_rate_limit=False 
    )
    return client
