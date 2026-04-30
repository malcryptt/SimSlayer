import tweepy
from core.tracker import already_targeted

def get_targets(client, keywords, verified_only=False, threads_only=False):
    """
    Search for recent tweets based on keywords and settings.
    client: tweepy.Client
    keywords: string of comma separated words
    verified_only: boolean
    threads_only: boolean
    Returns: list of tweepy.Tweet objects and their author dict mapped by author ID
    """
    if not keywords:
        return [], {}

    query_parts = []
    
    kws = [k.strip() for k in keywords.split(",") if k.strip()]
    if not kws:
        return [], {}
        
    kw_query = "(" + " OR ".join(kws) + ")"
    query_parts.append(kw_query)
    
    query_parts.append("-is:retweet")

    if verified_only:
        query_parts.append("is:verified")
        
    query = " ".join(query_parts)
    
    try:
        response = client.search_recent_tweets(
            query=query,
            max_results=50,
            tweet_fields=["created_at", "public_metrics", "author_id", "conversation_id"],
            expansions=["author_id"],
            user_fields=["created_at", "description", "profile_image_url", "public_metrics", "username"],
            sort_order="recency"
        )
        
        if not response.data:
            return [], {}
            
        tweets = response.data
        users = {u.id: u for u in response.includes.get('users', [])}
        
        results = []
        for tweet in tweets:
            if already_targeted(tweet.id):
                continue
                
            if threads_only:
                metrics = tweet.public_metrics
                reply_count = metrics.get('reply_count', 0)
                if reply_count == 0 and tweet.conversation_id == tweet.id:
                    if metrics.get('quote_count', 0) == 0:
                        continue
            
            results.append(tweet)
            
        return results, users
    except tweepy.TooManyRequests:
        raise
    except Exception as e:
        print(f"[Scanner Error] {e}")
        return [], {}
