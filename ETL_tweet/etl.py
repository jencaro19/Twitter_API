import pymongo 
from sqlalchemy import create_engine
import psycopg2
import time
#import cred
import re
import os 
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer




time.sleep(10)  # seconds

### create connections to databases (check your mongosb and postgres in python notebooks (or luftdaten))
# Establish a connection to the MongoDB server

client = pymongo.MongoClient(host="mongodb", port=27017)

# Select the database you want to use within the MongoDB server
db = client.tweet_db # name of db defined in the other python script
col_tweet = db.my_tweets # name of collection in the other py script


#Add postgres credentials
#the conncetion is not successful check for host(ip) or port 

port = 5432
host = 'postgresdb'
database = os.getenv('POSTGRES_DB')
user = os.getenv('POSTGRES_USER')
password = os.getenv('POSTGRES_PASSWORD')
#user = cred.user
#password = cred.password
#database = "twitter" 



# Establish a connection with Postgres

posg = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{database}', echo=True)

print(posg)

#posg = create_engine('postgresql://postgres:postgres@postgresdb:5432/twitter', echo=True)

# Clean your tweets
mentions_regex= '@[A-Za-z0-9]+'
url_regex='https?:\/\/\S+' #this will not catch all possible URLs
hashtag_regex= '#'
rt_regex= 'RT\s'

def clean_tweets(col):
    all_tweets = []
    for tweet in col.find():
        tweet_ats = re.sub(mentions_regex, '', tweet['text'])  #removes @mentions
        tweet_hash = re.sub(hashtag_regex, '', tweet_ats) #removes hashtag symbol
        tweet_annou = re.sub(rt_regex, '', tweet_hash) #removes RT to announce retweet
        tweet_url = re.sub(url_regex, '', tweet_annou) #removes most URLs # after all theprogression of cleaning 
                                                     # this is the one we append
    
        all_tweets.append(tweet_url)

    return all_tweets

cleaned = clean_tweets(col_tweet) #call on to the 'col_tweet' from mongodb


# Create the function that calculates polarity_scores and returns compund score
analyzer = SentimentIntensityAnalyzer()


def polarity_scores(all_cleaned_tweets):
    all_scores = []
    for tweet in all_cleaned_tweets:
       score = analyzer.polarity_scores(tweet)

       all_scores.append(score)

    return all_scores

scores = polarity_scores(cleaned) 


#Transform your tweets and create a dictionary

#create a dictionary
tweet_dic = {}
for tweets_score_index in range(0,len(cleaned)):
    tweet = cleaned[tweets_score_index]
    score = scores[tweets_score_index]
    tweet_dic[tweet] = float(score['compound']) # this is how you append for a dictionary for a list it is .append


posg.execute(f'''
    CREATE TABLE IF NOT EXISTS abor_tweets (
    text VARCHAR(500),
    sentiment NUMERIC
);
''')


#Load your tweets into a postgres database

#posg.to_sql('tweets', posg, if_exists='replace') # used only if we had placed our tweets in a df

# {
#     "My tweet sucks": 0.05
# }

for tweet_text, tweet_score in tweet_dic.items(): # items becuase we have 2 values one for key and one for score 
    
    query = "INSERT INTO abor_tweets VALUES (%s, %s);" # %s place holders 
    posg.execute(query, (tweet_text, tweet_score))


print("workflow twitter COMPLETE!!!")