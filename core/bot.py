import threading
import time
import random
import tweepy

from core.auth import get_tweepy_client
from core.scanner import get_targets
from core.detector import score_bot
from core.injector import get_payload
from core.tracker import log_shot, log_warning, get_warning_count_today, mark_hit

class SimSlayerBot:
    def __init__(self, gui_callback, stats_callback):
        self.running = False
        self.thread = None
        self.gui_callback = gui_callback  
        self.stats_callback = stats_callback 
        self.config = {}
        self.client = None

    def start(self, config):
        if self.running: return
        self.config = config
        self.running = True
        try:
            self.client = get_tweepy_client()
        except Exception as e:
            self.gui_callback("WARN ⚠", f"Auth Failed: {str(e)}")
            self.running = False
            return
            
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

    def _loop(self):
        self.gui_callback("SCAN", "Bot loop starting...")
        backoff_time = 60
        
        while self.running:
            self.gui_callback("SCAN", f"Searching targets for: {self.config['keywords']}")
            try:
                tweets, users = get_targets(
                    client=self.client,
                    keywords=self.config["keywords"],
                    verified_only=self.config["verified_only"],
                    threads_only=self.config["threads_only"]
                )
            except tweepy.TooManyRequests:
                self._handle_rate_limit(backoff_time)
                backoff_time = min(backoff_time * 2, 900)
                continue
            except Exception as e:
                self.gui_callback("WARN ⚠", f"Scanner error: {e}")
                self._sleep_with_jitter(60)
                continue

            backoff_time = 60 
            
            # hourly max check
            hourly_limit = int(self.config.get("max_replies", 12))
            
            for tweet in tweets:
                if not self.running: break
                
                author = users.get(tweet.author_id)
                if not author: continue
                
                score_data = score_bot(author)
                
                if score_data["is_bot"]:
                    self.gui_callback("TARGET", f"@{score_data['username']} scored {score_data['bot_score']}")
                    self._fire_payload(tweet, author)
                else:
                    self.gui_callback("SCAN", f"Skipping @{score_data['username']}, low score")
                
                self._sleep_with_jitter(10)
                self.stats_callback()

            self._check_for_hits()
            
            warn_count = get_warning_count_today()
            if warn_count > 5:
                self.gui_callback("WARN ⚠", "High Suspension Risk! (Warnings > 5 today)")
            
            interval = max(60, int(self.config.get("interval", 60)))
            self._sleep_with_jitter(interval)
            
    def _fire_payload(self, target_tweet, author):
        payload_id, payload_text = get_payload()
        if not payload_id:
            self.gui_callback("WARN ⚠", "No payloads available to inject.")
            return

        try:
            response = self.client.create_tweet(
                text=payload_text,
                in_reply_to_tweet_id=str(target_tweet.id)
            )
            
            if response and response.data:
                our_reply_id = str(response.data['id'])
                log_shot(author.username, str(target_tweet.id), payload_id, payload_text, our_reply_id)
                self.gui_callback("SENT", f"Payload sent to @{author.username}")
                self.stats_callback()
        except tweepy.TooManyRequests:
            self.gui_callback("WARN ⚠", "Rate limit hit while posting.")
            log_warning("RATE_LIMIT", "Tweet creation rate limit hit")
            self._sleep_with_jitter(60)
        except tweepy.Forbidden:
            self.gui_callback("WARN ⚠", "Account suspended or forbidden from replying.")
            log_warning("SUSPENSION_RISK", "Received 403 Forbidden on reply")
            self.stop()
        except Exception as e:
            self.gui_callback("WARN ⚠", f"Error posting: {e}")

    def _check_for_hits(self):
        try:
            me = self.client.get_me()
            if not me or not me.data: return
            
            query = f"to:{me.data.username} \"Check out Simcluster\""
            res = self.client.search_recent_tweets(query=query, max_results=10, tweet_fields=["in_reply_to_tweet_id"])
            if res.data:
                for t in res.data:
                    if t.in_reply_to_tweet_id:
                        mark_hit(str(t.in_reply_to_tweet_id))
                        self.gui_callback("HIT ✓", f"Hit detected from tweet checking Simcluster!")
                        self.stats_callback()
        except Exception:
            pass

    def _handle_rate_limit(self, backoff):
        self.gui_callback("WARN ⚠", f"Rate limit hit. Backing off {backoff}s...")
        log_warning("API_LIMIT", f"Rate limit hit on search, backed off {backoff}s")
        self._sleep_with_jitter(backoff)

    def _sleep_with_jitter(self, base_seconds):
        if base_seconds < 60:
            pass 
        jitter = base_seconds * random.uniform(0.10, 0.15)
        time.sleep(base_seconds + jitter)
