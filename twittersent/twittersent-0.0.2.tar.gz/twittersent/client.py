"""

-----   module::
         :platform: Mac OSX, Unix
         :python --version: 3.5


-----   author:: Shekhar Jha <shekhar09jha@gmail.com>


"""

import twitter
import pandas as pd
import re
from textblob import TextBlob
import seaborn as sns


api = twitter.Api(consumer_key=None,
                  consumer_secret=None,
                  access_token_key=None,
                  access_token_secret=None)


class TwitterSent(object):

    def clean_tweet(self, tweet):
        '''
        Utility function to clean tweet text by removing links, special characters
        using simple regex statements.
        '''
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) |(\w+:\/\/\S+)", " ", tweet).split())


    def get_tweet_sentiment(self, tweet):
        '''
        Utility function to classify sentiment of passed tweet
        using textblob's sentiment method
        '''
        # create TextBlob object of passed tweet text
        analysis = TextBlob(self.clean_tweet(tweet))
        # set sentiment
        if analysis.sentiment.polarity > 0:
            return 'positive'
        elif analysis.sentiment.polarity == 0:
            return 'neutral'
        else:
            return 'negative'


    def get_min_max(self, tweets):
        ids = []
        for tweet in tweets:
            # print tweet
            if type(tweet) is list:
                tweet = tweet[0]
            ids.append(tweet.id)
        min_id = min(ids)
        max_id = max(ids)
        return min_id, max_id


    def get_tweets(self, term, count):
        all_tweets = []
        max_id = 843567375765159939000000
        #print max_id
        loop_count = int(count / 100)
        for i in range(loop_count):
            tweets = api.GetSearch(term=term, count = 100)
            #print 'Total number of tweets found - '  +  str(len(tweets))
            try:
                min_id, max_id = self.get_min_max(tweets)
                all_tweets = all_tweets + tweets
            except:
                print ('something wrong')
                pass
        return all_tweets


    def get_tweets_df(self, tweets):
        result = []
        for tweet in tweets:
            favorite_count = tweet.favorite_count
            retweet_count = tweet.retweet_count
            source = tweet.source
            text = tweet.text
            urls = tweet.urls
            sentiment = self.get_tweet_sentiment(text)

            result.append({
                #'text': base64.b64encode(text.encode('ascii', 'ignore').decode('ascii')),
                'text': text.encode('ascii', 'ignore').decode('ascii'),
                'sentiment': sentiment,
                'favorite_count' : favorite_count,
                'source' : source,
                'retweet_count' : retweet_count,
                'user_fav_count': tweet.user.favourites_count,
                'user_follower_count': tweet.user.followers_count,
                'user_friends_count': tweet.user.friends_count,
                'user_screen_name' : tweet.user.screen_name.encode('ascii', 'ignore').decode('ascii'),
                'user_name': tweet.user.name.encode('ascii', 'ignore').decode('ascii'),
                'user_url': tweet.user.url
            })
        result_df = pd.DataFrame(result)
        return result_df


    def print_tweet(self, tweet):
        print ('---- Printing tweet ----')
        print ("Likes: ", tweet.favorite_count)
        print (tweet.text)
        print (' --------- x --------- ')


    #################################################
    ####          SENTIMENT CALCULATION          ####
    #################################################

    def calculate_sentiment(self, my_list, total_number_of_tweets ):
        """
        Calculate the sentimate of each item from the input list
        :tweets_person: list of the tweets related to the object
        """

        for i in my_list:
            print("Fetching tweets for %s" % i)
            tweets_person = self.get_tweets(i, total_number_of_tweets)
            print("Total number of tweets fetched = " + str(len(tweets_person)))
            df_person = self.get_tweets_df(tweets_person)
            sentiment_person = df_person.groupby(['sentiment'])[['sentiment']].count()
            sentiment_person.rename(columns={'sentiment': i}, inplace=True)
            return sentiment_person


    #################################################
    ####                   PLOTS                 ####
    #################################################

    def barplot(self, sentiment_person):
        """
        Returns the bar plot with positive, negative and neutral on x-axis
        and number of tweets for each of the three categories on y-axis

        """

        # temporary variable to store the sentiment of each object of the list
        temp = sentiment_person
        print(temp)
        temp.plot(kind = 'bar')
        sns.plt.show()
