import datetime
import re

def score_bot(user_data):
    """
    Scoring algorithm for bot detection based on user criteria.
    user_data: dict of user data from tweepy
    Score 0-100 threshold > 40 is a target.
    Returns: dict with score assessment
    """
    score = 0
    reasons = []

    # Requires user_data to have created_at, profile_image_url, username, description, public_metrics fields loaded

    # Account age < 1 year: +20
    if user_data.get('created_at'):
        created_at = user_data.get('created_at')
        if isinstance(created_at, str):
            try:
                # Handle ISO 8601 string safely
                created_at = datetime.datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            except Exception:
                pass

        if isinstance(created_at, datetime.datetime):
            # Make now aware if created_at is aware
            now = datetime.datetime.now(datetime.timezone.utc)
            age_in_days = (now - created_at).days
            if age_in_days < 365:
                score += 20
                reasons.append("Account age < 1 year (+20)")
        else:
            age_in_days = -1
    else:
        age_in_days = -1

    # No profile picture: +15
    # If the user has "default_profile_images" in URL
    profile_img = user_data.get('profile_image_url', "")
    if "default_profile_images" in profile_img:
        score += 15
        reasons.append("Default profile picture (+15)")

    username = user_data.get('username', "")
    if username:
        if re.search(r'\\d{4,}', username) or re.search(r'[a-zA-Z0-9]{15,}', username):
            score += 15
            reasons.append("Username contains numbers/random chars (+15)")

    desc = user_data.get('description', "")
    if desc:
        desc_lower = desc.lower()
        if any(keyword in desc_lower for keyword in [" ai ", "bot", "gpt", "assistant"]):
            score += 25
            reasons.append("Bio contains AI/bot keywords (+25)")

    metrics = user_data.get('public_metrics', {})
    tweet_count = metrics.get('tweet_count', 0)
    
    if age_in_days > 0:
        tweets_per_day = tweet_count / age_in_days
        if tweets_per_day > 100:
            score += 5
            reasons.append("Tweet volume > 100/day (+5)")

    return {
        "account_id": user_data.get('id'),
        "username": username,
        "bot_score": min(100, score),
        "reasons": reasons,
        "is_bot": score > 40
    }
