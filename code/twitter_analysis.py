import os
import re
import pandas as pd
import tweepy as tw
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
        auth = tw.OAuthHandler(self.keys['consumer_key'], self.keys['consumer_secret'])
        auth.set_access_token(self.keys['access_token'], self.keys['access_token_secret'])
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

    def dataWrangling(self, dropCols = [], geocode = True, savefile=True, save_location='export/'):
        '''
        This method geocodes the location information of the dataframe and process/drops other columns
        If no location is given the value is empty, therefore first it drops these rows.
        The process could take up to 20 mins.
        Returns geocoded dataframe
        '''
        start_time = time.time()
        wranglingDF = self.dataframe
        wranglingDF.replace("", float("NaN"), inplace=True) # replace empty values with NaN value
        wranglingDF.dropna(subset=['location'], inplace=True) # drop rows where location is NaN

        # Geocoding
        if geocode:
            print(f"Geocoding {wranglingDF.shape[0]} values. Please stand by...")
            wranglingDF['geocoded_loc'] = wranglingDF['location'].apply(self.geocode) # Geocoding data
        else:
            print("Geocoding off")

        # Drop -1 values of geocoded_loc
        wranglingDF.drop(wranglingDF[wranglingDF['geocoded_loc']=='-1'].index, inplace=True)
        # Process creation_time column
        wranglingDF['date'] = [d.date() for d in wranglingDF['creation_time']]
        wranglingDF['time'] = [d.time() for d in wranglingDF['creation_time']]

        # Drop columns we don't need for further analysis
        if dropCols:
            wranglingDF.drop(dropCols, axis=1, inplace=True)
        else:
            wranglingDF.drop(['creation_time'], axis=1, inplace=True)

        wranglingDF.reset_index(drop=True, inplace=True) # Reset indexing in the dataframe

        for i in range(len(wranglingDF['text'])):
            wranglingDF['text'][i] = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", wranglingDF['text'][i]).split())
        
        # Save processed file to json
        if savefile:
            if not os.path.exists(save_location):
                os.mkdir(save_location)
            wranglingDF.to_json(f'{save_location}/processed_data.json', orient='columns', indent=2)
            print(f'Geocoded file saved to {save_location}/processed_data.json')

        # Measure processing time for processing
        print(f'Elapsed time: {(time.time()-start_time):.2f} sec')
        return wranglingDF

class dataAnalysis:
    def __init__(self, dataframe):
        self.dataframe = dataframe

    def twitterEDA(self, keyword, showFigure = True, saveFigure = False, savePath = 'export/'):
        '''
        displays graphs of location distribution, tweet count, time, device
        '''
        edaDF = self.dataframe

        # Import necessary libraries to make visualizations
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        lat = [edaDF['geocoded_loc'][i][0] for i in range(edaDF['geocoded_loc'].shape[0])]
        lon = [edaDF['geocoded_loc'][i][1] for i in range(edaDF['geocoded_loc'].shape[0])]

        # Config subplots
        fig = make_subplots(
            rows = 2, cols = 2,
            column_widths = [0.7, 0.3],
            row_heights = [0.5, 0.5],
            specs = [
                [{"type":"scattergeo", "rowspan":2}, {"type":"scatter"}],
                [               None               , {"type":"bar"}]
            ]
        )

        # Add map trace with scatterplot
        fig.add_trace(
            go.Scattergeo(
                lat = lat,
                lon = lon,
                mode = "markers",
                hoverinfo = "text",
                #showlegend = False,
                marker = dict(
                    color = "crimson",
                    size = 4,
                    opacity = 0.8
                )
            ),
            row = 1, col = 1
        )
        # Config map
        fig.update_geos(
            projection_type = "mercator",
            showcoastlines = True,
            showcountries=True,
            showland = True, #landcolor = "rgb(212, 212, 212)",
            showocean = True, oceancolor = "white",
            showlakes = True, #lakecolor = "LightGray",
            showrivers = True, #rivercolor = "LightGray",
            framecolor = "white",
            uirevision = True
        )

        # Config layout
        fig.update_layout(
            mapbox_style="open-street-map",
            margin=dict(r=0, t=30, b=0, l=0),
            title=f'Tweets with {keyword} hashtag',
            showlegend = False,
            dragmode = 'pan'
        )

        # Add scatterplot with line of tweet count vs time
        fig.add_trace(
            go.Scatter(
                x = edaDF['date'].unique(),
                y = edaDF['date'].value_counts(),
                marker = dict(color="crimson"),
                showlegend = False
            ),
            row = 1, col = 2
        )

        # Add bar plot of source devices
        fig.add_trace(
            go.Bar(
                x = edaDF['source_device'].unique()[:10],
                y = edaDF['source_device'].value_counts(),
                marker = dict(color="crimson"),
                showlegend = False
            ),
            row = 2, col = 2
        )

        if saveFigure:
            if not os.path.exists(savePath):
                os.mkdir(savePath)
            fig.write_html(os.path.join(savePath, 'eda_export.html'))
            fig.write_image(os.path.join(savePath, 'eda_export.png'))
            print(f'Figure saved to: {savePath}')
        
        if showFigure:
            fig.show()

        return fig

    def twitterSentimentAnalysis(self, saveFile = False, savePath = 'export/'):
        from textblob import TextBlob
        sentimentDF = self.dataframe
        sentiments = []
        
        for i in range(len(sentimentDF['text'])):
            tweet = sentimentDF['text'][i]
            analysis = TextBlob(tweet)
            if analysis.sentiment.polarity > 0:
                sentiments.append('Positive')
            elif analysis.sentiment.polarity == 0:
                sentiments.append('Neutral')
            else:
                sentiments.append('Negative')
        sentimentDF['sentiment'] = sentiments

        # Save processed dataframe to json
        if saveFile:
            if not os.path.exists(savePath):
                os.mkdir(savePath)
            sentimentDF.to_json(f'{savePath}/processed_SA_data.json', orient='columns', indent=2)
            print(f'Geocoded file saved to {savePath}/processed_SA_data.json')

        return sentimentDF

# data visualisation >> plotly dashboard/tableu dashboard

if __name__ == '__main__':
    
    # Acces keys
    keys = {
        'consumer_key' : 'tw6NVxVJ1z0RYQLxy7mnOyGSN',
        'consumer_secret' : 'teR9ivG8yybmgpSlsjGXzrb3bFDHcwsVGK56CJZoxf1YSfKTFx',
        'access_token' : '4643374648-8BZhoJc9jIL0QEfbQ2niswvXlOIUrQyoxxP6UhM',
        'access_token_secret' : '1lZcdkU4svzYNhFJWdyXxMOV2Kv13jEGAF0QmigGy6VX7'
    }

    # Init data collection
    searchHashtags = '#mcdonalds'
    '''
    object = twitterDataCollection(
        keys,
        searchTerm=searchHashtags,
        tweetCount=100,
        sinceDate='2022-05-01'
    )
    # Collect tweets into dataframe
    df = object.collectTweets()

    # Export tweets into JSON file
    object.exportTweetsToJSON(df, save_location='export/', filename='twitter_original_data', format='JSON')
    '''
    df = pd.read_json('../data/geocoded_data.json')
    # Data wrangling and geocoding
    twitter_wrangling = dataPrep(df)
    df2 = twitter_wrangling.dataWrangling(dropCols=['creation_time', 'hashtags', 'status_count', 'name', 'screen_name'], geocode=False)

    # Analyse processed data
    tweet_analysis = dataAnalysis(df2)
    #tweet_analysis.twitterEDA(searchHashtags, showFigure=True,savePath='export/', saveFigure=True)
    
    df_analysed = tweet_analysis.twitterSentimentAnalysis()

    print(df_analysed.head())


