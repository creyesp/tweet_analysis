import argparse
from datetime import datetime
import json
import logging
import os
from pathlib import Path


import tweepy
from pymongo import MongoClient

MONGO_CONN = MongoClient('127.0.0.1')
TWEET_DB = MONGO_CONN['tweet_raw']
TW_COLLECTION = TWEET_DB['tweets']
logging.basicConfig(level=logging.INFO)


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--track',
                        help='list of keyword',
                        type=list)
    parser.add_argument('--user_id',
                        help='list of user_id',
                        type=list)
    parser.add_argument('--lang',
                        help='filter by lenguage. ex "es"',
                        type=list)
    args = parser.parse_args()
    return args

def get_twitter_api(keys):
    with open(keys) as f:
        credentials = json.load(f)

    auth = tweepy.OAuthHandler(credentials['consumer_key'],
                               credentials['consumer_secret'])
    auth.set_access_token(credentials['token'], credentials['token_secret'])
    api = tweepy.API(auth,
                     wait_on_rate_limit=True,
                     wait_on_rate_limit_notify=True,
                     timeout=60 * 5, )
    return api


class UyStreamListener(tweepy.StreamListener):

    def __init__(self, *args, save_to='mongo', **kwargs):
        super().__init__(*args, **kwargs)
        self.save_to = save_to

    def on_status(self, status):
        # XXX: We could add some filter before to storage tweet
        logging.info(f'New Tweet by {status.user.screen_name:<15} at {status.created_at}')
        if self.save_to == 'mongo':
            self._to_mongo(status)
        else:
            self._to_json(status)

        return True

    def on_error(self, status_code):
        if status_code == 420:
            # returning False in on_error disconnects the stream
            # returning non-False reconnects the stream, with backoff.
            return False

    @staticmethod
    def _to_json(status):
        storage = f'{datetime.now().strftime("%Y-%m-%d")}.json'
        try:
            with open(storage, 'a') as f:
                f.write('\n')
                json.dump(status._json, f)
        except Exception as e:
            logging.info(f'Error on_data: {e}')

    @staticmethod
    def _to_mongo(status):
        data = status._json
        data['_id'] = data['id_str']
        try:
            TW_COLLECTION.insert_one(data)
        except Exception as e:
            logging.info(f'Error on_data: {e}')


if __name__ == '__main__':
    path = Path(os.path.realpath(__file__))
    credential_path = os.path.join(
        path.parent.parent, 'credentials', 'twitter_credentials.json')
    api = get_twitter_api(keys=credential_path)
    myStream = tweepy.Stream(auth=api.auth,
                             listener=UyStreamListener(save_to='mongo'))

    args = get_arguments()
    track = args.track
    user_id = args.user_id
    lang = args.lang

    myStream.filter(follow=user_id,
                    track=track,
                    is_async=False,
                    locations=None,
                    stall_warnings=False,
                    languages=lang,
                    encoding='utf8',
                    filter_level=None, )
