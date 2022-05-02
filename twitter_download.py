import os
import pandas as pd
import tweepy as tw
import numpy as np

# Acces keys
keys = {
    'consumer_key' : 'tw6NVxVJ1z0RYQLxy7mnOyGSN',
    'consumer_secret' : 'teR9ivG8yybmgpSlsjGXzrb3bFDHcwsVGK56CJZoxf1YSfKTFx',
    'access_token' : '4643374648-8BZhoJc9jIL0QEfbQ2niswvXlOIUrQyoxxP6UhM',
    'access_token_secret' : '1lZcdkU4svzYNhFJWdyXxMOV2Kv13jEGAF0QmigGy6VX7'
}

class twitterDataCollection:
    def __init__(self, keys, searchTerm, tweetCount):
        self.keys = keys
        self.searchTerm = searchTerm
        self.tweetCount = tweetCount

    def twitterAuth(self):
        auth = tw.OAuthHandler(keys['consumer_key'], keys['consumer_secret'])
        auth.set_access_token(keys['access_token'], keys['access_token_secret'])
        api = tw.API(auth, wait_on_rate_limit=True)
        return api

    def collectTweets(self, api):
        # Define the search term and the date as variables
        # search_words = "#burgerking"
        # date_since = "2022-01-01"

        # Collect tweets
        results = api.search_tweets(
            q=self.searchTerm,
            lang='en',
            count=self.tweetCount,
            tweet_mode='extended'
            )

        # Organise collected tweets
        data = []
        for item in results:
            mined = {
                'tweet_id':        item.id,
                'name':            item.user.name,
                'screen_name':     item.user.screen_name,
                'retweet_count':   item.retweet_count,
                'text':            item.full_text,
                'created_at':      item.created_at,
                'favourite_count': item.favorite_count,
                'hashtags':        item.entities['hashtags'],
                'status_count':    item.user.statuses_count,
                'location':        item.place,
                'source_device':   item.source
                }
            data.append(mined)

        # Save tweets to dataframe
        df = pd.DataFrame(data)
        # print(df.head())
        return df
    
    def dataWrangling(self):
        pass

# https://www.earthdatascience.org/courses/use-data-open-source-python/intro-to-apis/twitter-data-in-python/

object = twitterDataCollection(
    keys,
    searchTerm='#burgerking',
    tweetCount=10
)

api = object.twitterAuth()
df = object.collectTweets(api)
print(df.head())

# Export dataframe to json
if not os.path.exists(r'json_export/'):
    os.mkdir(r'json_export/')

# Save dataframe to JSON file
df.to_json(r'json_export/twitter_data.json')
