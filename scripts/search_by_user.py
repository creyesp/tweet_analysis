from datetime import datetime
import json
import tweepy
import logging

logging.basicConfig(level=logging.INFO)


def _retrieve_tweet(tweet):
    tweet_data = tweet._json
    return tweet_data


def search_word(search_txt, n_items=None, until_date=None,
                latitide=None, longitude=None, radius=None, verbose=True, **kwargs):
    """Retrieve tweets."""
    if latitide and longitude and radius:
        uy_tweets = tweepy.Cursor(api.search,
                                  q=search_txt,
                                  until=until_date,
                                  geocode=f"{latitide},{longitude},{radius}km",
                                  tweet_mode='extended',
                                  **kwargs,
                                  )
    else:
        uy_tweets = tweepy.Cursor(api.search,
                                  q=search_txt,
                                  until=until_date,
                                  tweet_mode='extended',
                                  **kwargs)

    tweets = []
    try:
        if n_items:
            for idx, tweet in enumerate(uy_tweets.items(n_items)):
                tweets.append(_retrieve_tweet(tweet))
                if not idx % 100:
                    print(f'retrieve {idx} tweets')
        else:
            for idx, tweet in enumerate(uy_tweets.items()):
                tweets.append(_retrieve_tweet(tweet))
                if not idx % 100:
                    print(f'retrieve {idx} tweets')
    except Exception as e:
        logging.info('Unexpected error, returning partials tweets')

    return tweets


if __name__ == '__main__':
    keys = [
        '@eajpnv',
        '@iurkullu',
        '@MaddalenIriarte',
        '@ehbildu',
        '@PodemosEuskadi_',
        '@MiGorrotxategi',
        '@socialistavasco',
        '@IdoiaMendia',
        '@PPVasco',
        '@Cs_Euskadi',
        '@carlositurgaiz',
        '@EquoBerdeak',
        '@JoseRa_Becerra',
        '@vox_guipuzcoa',
        '@vox_alava',
        '@vox_bilbao',
    ]
    with open('../credentials/twitter_credentials.json') as f:
        credentials = json.load(f)

    auth = tweepy.OAuthHandler(credentials['consumer_key'], credentials['consumer_secret'])
    auth.set_access_token(credentials['token'], credentials['token_secret'])
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, timeout=60*5,)

    n_items = 500
    data = {user: [status._json for status in
                   tweepy.Cursor(api.user_timeline, screen_name=user, tweet_mode="extended").items(n_items)] for user in
            keys}
    with open(f'../data/raw/euskera_{datetime.now()}.json', 'w') as f:
        json.dump(data, f)