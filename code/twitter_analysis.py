import os
import pandas as pd
import tweepy as tw
import numpy as np
import requests
import urllib
import time

class twitterDataCollection:
    def __init__(self, keys, searchTerm, tweetCount, sinceDate):
        self.keys = keys
        self.searchTerm = searchTerm
        self.tweetCount = tweetCount
        self.sinceDate = sinceDate

    def twitterAuth(self):
        '''
        This method initialize the twitter api with the given keys
        Returns API
        '''
        auth = tw.OAuthHandler(keys['consumer_key'], keys['consumer_secret'])
        auth.set_access_token(keys['access_token'], keys['access_token_secret'])
        api = tw.API(auth, wait_on_rate_limit=True)
        return api

    def collectTweets(self):
        '''
        This method collects tweets of a gives search term, time and count
        Returns dataframe with collected data
        '''
        # Get the API
        api = self.twitterAuth()
        # Collect tweets
        results = tw.Cursor(api.search_tweets,
            q=self.searchTerm,
            lang='en',
            count=self.tweetCount,
            tweet_mode='extended',
            since_id=self.sinceDate
            )

        # Organise collected tweets
        data = []
        for item in results.items():
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
                'location':        item.user.location,
                'source_device':   item.source,
                'creation_time':   item.created_at
                }
            data.append(mined)

        # Save tweets to dataframe
        df = pd.DataFrame(data)
        return df

    def exportTweetsToJSON(self, dataframe, save_location, filename, format):
        '''
        This method exports the created dataframe to json or csv file at a given
        path.
        '''
        # Check if give path exist, if not it creats it
        if not os.path.exists(save_location):
            os.mkdir(save_location)

        if format=='JSON':
            # Save dataframe to JSON file
            dataframe.to_json(f'{save_location}/{filename}.json', orient='columns', indent=2)
            return print(f"File saved to {save_location}/{filename}.json")

        elif format=='CSV':
            # Save dataframe to CSV file
            dataframe.to_csv(f"{save_location}/{filename}.csv", header=True)
            return print(f"File saved to {save_location}/{filename}.csv")

class dataPrep:
    def __init__(self, dataframe):
        self.dataframe = dataframe

    def geocode(self, locality):
        url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(locality) +'?format=json'
        response = requests.get(url).json()
        if len(response)!=0:
            return (response[0]['lat'], response[0]['lon'])
        else:
            return ('-1')

    def dataWrangling(self, savefile=True, save_location='geocoded_export/'):
        '''
        This method geocodes the location information of the dataframe
        If no location is given the value is empty, therefore first it drops these rows.
        The process could take up to 20 mins.
        Returns geocoded dataframe
        '''
        start_time = time.time()
        self.dataframe = df
        df.replace("", float("NaN"), inplace=True) # replace empty values with NaN value
        df.dropna(subset=['location'], inplace=True) # drop rows where location is NaN
        df.reset_index(drop=True, inplace=True) # Reset indexing in the dataframe
        # Geocoding
        print(f"Geocoding {df.shape[0]} values. Please stand by...")
        df['geocoded_loc'] = df['location'].apply(self.geocode) # Geocoding data

        # Drop -1 values of geocoded_loc
        

        # Process time column

        # Save processed file to json
        if savefile:
            if not os.path.exists(save_location):
                os.mkdir(save_location)
            df.to_json(f'{save_location}/processed_data.json', orient='columns', indent=2)
            print(f'Geocoded file saved to {save_location}/processed_data.json')
        # Measure processing time for processing
        print(f'Elapsed time: {(time.time()-start_time):.2f} sec')
        return df

class dataAnalysis:
    def __init__(self, dataframe):
        self.dataframe = dataframe

    def twitterEDA(self):
        '''
        displays graphs of location distribution, retweet count, time, device
        '''
        pass

    def twitterSentimentAnalysis(self):
        pass


# data visualisation >> plotly dashboard/tableu dashboard

if __name__ == '__main__':
    '''
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
        searchTerm='#mcdonalds',
        tweetCount=100,
        sinceDate='2022-05-01'
    )
    # Collect tweets into dataframe
    df = object.collectTweets()

    # Export tweets into JSON file
    object.exportTweetsToJSON(df, save_location='json_export/', filename='twitter_data', format='JSON')
    '''
    df = pd.read_json(r'json_export//twitter_data.json')
    print(df)
    twitter_wrangling = dataPrep(df)
    df2 = twitter_wrangling.dataWrangling()
    print(df2)
