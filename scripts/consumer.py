import base64
import json
import sys

from google.cloud import bigquery

DATASET = 'social-thermometer-dev.test_pipeline'
TABLE = 'uy_tweet_test'


def pubsub_to_bq(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    if 'data' in event:
        pubsub_message = base64.b64decode(event['data']).decode('utf-8')
        to_bigquery(DATASET, TABLE, json.loads(pubsub_message))



def to_bigquery(dataset, table, document):
    bq_client = bigquery.Client()
    table = bq_client.get_table(f'{dataset}.{table}')
    rows = [(
        document['text'],
        document['user_id'],
        document['id'],
        document['posted_at'],
    )]
    errors = bq_client.insert_rows(table, rows)
    if errors:
        print(errors, file=sys.stderr)
