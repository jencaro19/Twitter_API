import tweepy
#import twitter_keys
import pymongo
import os # only when using .env file for passwords or tokens in this case
 
# bear_token = twitter_keys.BEARER_TOKEN
# bear = tweepy.Client(bearer_token= bear_token)

bear_token = os.getenv('BEARER_TOKEN')
bear = tweepy.Client(bearer_token=bear_token)

client = pymongo.MongoClient('mongodb', port=27017)      # establish connection to client
                                                        # if only one client is running:


# define db 
db = client.tweet_db # 'my_db' is name of db

# define collection
dbcoll = db.my_tweets # includes database and collection name

def tweet_app():
    search_query = "#abortion -is:retweet -is:reply -is:quote -has:links lang:en"

    cursor = tweepy.Paginator(
        method=bear.search_recent_tweets,
        query=search_query,
        tweet_fields=['author_id', 'created_at', 'public_metrics'],
        user_fields=['username'],
    ).flatten(limit=200)

    for tweet in cursor:
        print(tweet.data)
        dbcoll.insert_one(tweet.data) # fake_doc is document


    # with open('abortion_tweets.txt', 'a', encoding='utf-8') as f:
    #     for tweet in cursor:
    #         f.writelines(str(tweet.data['text']))
                   
if __name__ == "__main__":
    tweet_app()