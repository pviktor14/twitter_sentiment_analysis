import os
import pandas as pd
import tweepy as tw
import numpy as np

class twitterDataCollection:
    def __init__(self, keys, searchTerm, tweetCount, sinceDate):
        self.keys = keys
        self.searchTerm = searchTerm
        self.tweetCount = tweetCount
        self.sinceDate = sinceDate

    def twitterAuth(self):
        auth = tw.OAuthHandler(keys['consumer_key'], keys['consumer_secret'])
        auth.set_access_token(keys['access_token'], keys['access_token_secret'])
        api = tw.API(auth, wait_on_rate_limit=True)
        return api

    def collectTweets(self):
        api = self.twitterAuth()
        # Define the search term and the date as variables
        # search_words = "#burgerking"

        # Collect tweets
        results = api.search_tweets(
            q=self.searchTerm,
            lang='en',
            count=self.tweetCount,
            tweet_mode='extended',
            since_id=self.sinceDate
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
                'source_device':   item.source,
                'creation_time':   item.created_at
                }
            data.append(mined)

        # Save tweets to dataframe
        df = pd.DataFrame(data)
        return df
    def exportTweetsToJSON(self, save_location):
        # Export dataframe to json
        if not os.path.exists(save_location):
            os.mkdir(save_location)
        # Save dataframe to JSON file
        df.to_json(r'json_export/twitter_data.json')
        return print(f"File saved to {save_location}/twitter_data.json")

class dataPrep:
    def __init__(self, dataframe):
        self.dataframe = dataframe

    def geocodeLocations(self):
        pass
        # https://automating-gis-processes.github.io/CSC18/lessons/L3/geocoding.html
        # https://www.natasshaselvaraj.com/a-step-by-step-guide-on-geocoding-in-python/

    def convertTime(self):
        pass


# https://www.earthdatascience.org/courses/use-data-open-source-python/intro-to-apis/twitter-data-in-python/
if __name__ == '__main__':
    # Acces keys
    keys = {
        'consumer_key' : 'tw6NVxVJ1z0RYQLxy7mnOyGSN',
        'consumer_secret' : 'teR9ivG8yybmgpSlsjGXzrb3bFDHcwsVGK56CJZoxf1YSfKTFx',
        'access_token' : '4643374648-8BZhoJc9jIL0QEfbQ2niswvXlOIUrQyoxxP6UhM',
        'access_token_secret' : '1lZcdkU4svzYNhFJWdyXxMOV2Kv13jEGAF0QmigGy6VX7'
    }
    # Init data collection
    object = twitterDataCollection(
        keys,
        searchTerm='#burgerking',
        tweetCount=10,
        sinceDate='2022-01-01'
    )
    # Collect tweets into dataframe
    df = object.collectTweets()
    print(df.head())
    object.exportTweetsToJSON(save_location='json_export/')
