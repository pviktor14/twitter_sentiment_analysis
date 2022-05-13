# Customer satisfaction analysis with Twitter API using Python

This project showcase a method that can be used to measure the customer satisfaction towards a brand, event or service.

## Project overview
The data is collected via Twitter RESTAPI and python library tweepy. The collected tweets saved to pandas dataframe and json file.

After the data collected it was necessary to implement a data preparation phase, because of the various data formats and the location data needed to be geocoded to longitude and latitude data do geospatial analysis as well.

The goal of the project is to determine what is the satisfactory level of a certain product based on tweets. So I had to make text sentiment analysis. Through that I rated the tweet of a particular user from -1 - +1 (-1: negative, 0: neutral, +1: positive), than I summed up each user's opinion. After that I classified the users and proceed with other analysis which included geospatial analysis (to see which region of the world is more positive). I also aimed to determine the loyality of the users in specific regions.

I provide a Jupyter Notebook to explain each step of the project with outputs to represent my findings, but I also include the source codes.

## TODO
Collect data before Volt festival, the last day of the festival and after the festival!
Analyse the collected data.
