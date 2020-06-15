# pip install –upgrade google-cloud-pubsub
import json
import logging
from datetime import datetime
import time
from tweepy import API, OAuthHandler, Stream
from tweepy.streaming import StreamListener
from google.cloud import pubsub_v1

logging.basicConfig(level=logging.INFO)

ENV = 'dev'
PROJECT_NAME = f'social-thermometer-{ENV}'
TOPIC_NAME = 'uy_tweets'
CREDENTIAL_PATH = '../credentials/twitter_credentials.json'
GCP_CREDENTIAL_PATH = '../credentials/social-thermometer-dev-f2b953ed1da1.json'
publisher_client = pubsub_v1.PublisherClient()
topic_path = publisher_client.topic_path(PROJECT_NAME, TOPIC_NAME)


def setup_api(credentials: dict):
    auth = OAuthHandler(credentials['consumer_key'], credentials['consumer_secret'])
    auth.set_access_token(credentials['token'], credentials['token_secret'])
    api_twitter = API(auth,
                      wait_on_rate_limit=True,
                      wait_on_rate_limit_notify=True,
                      timeout=60 * 5, )
    return api_twitter


class UyStreamListener(StreamListener):

    def __init__(self, *args, save_to='pubsub', **kwargs):
        super().__init__(*args, **kwargs)
        self.save_to = save_to

    def on_status(self, status):
        # XXX: We could add some filter before to storage tweet
        logging.info(f'New Tweet by {status.user.screen_name:<15} at {status.created_at}')
        if self.save_to == 'pubsub':
            self._to_pubsub(status._json)
        else:
            self._to_json(status._json)

        return True

    def on_error(self, status_code):
        if status_code == 420:
            # returning False in on_error disconnects the stream
            # returning non-False reconnects the stream, with backoff.
            return False

    @staticmethod
    def _to_json(data):
        storage = f'{datetime.now().strftime("%Y-%m-%d")}.json'
        try:
            with open(storage, 'a') as f:
                f.write('\n')
                json.dump(data, f)
        except Exception as e:
            logging.info(f'Error on_data: {e}')

    @staticmethod
    def _to_mongo(data):
        data['_id'] = data['id_str']
        try:
            # TW_COLLECTION.insert_one(data)
            pass
        except Exception as e:
            logging.info(f'Error on_data: {e}')

    @staticmethod
    def _to_pubsub(data):
        try:
            # publish to the topic, don't forget to encode everything at utf8!
            selected_fields = json.dumps({
                "text": data["text"],
                "user_id": data["user"]["screen_name"],
                "id": data["id_str"],
                #"posted_at": datetime.fromtimestamp(data["created_at"]).strftime('%Y-%m-%d %H:%M:%S'),
                "posted_at": time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(data['created_at'],'%a %b %d %H:%M:%S +0000 %Y')),
            }).encode("utf-8")
            publisher_client.publish(topic_path, data=selected_fields, tweet_id=str(data["id"]).encode("utf-8"))
            print(selected_fields)
        except Exception as e:
            print(e)
            raise


if __name__ == '__main__':
    credentian_gcp = ''
    credentian_tw = ''
    with open(CREDENTIAL_PATH) as f:
        credentials_tw = json.load(f)
    api = setup_api(credentials_tw)

    twitterStream = Stream(auth=api.auth, listener=UyStreamListener())
    twitterStream.filter(track=['uruguay'])
