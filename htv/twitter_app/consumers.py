import json
import logging
from time import sleep

from channels import Group
from channels.sessions import channel_session

from twitter_app.api import TwitterAPI
from twitter_app.models import Topic, Tweet


# Get an instance of a logger
logger = logging.getLogger('htv')


@channel_session
def ws_connect(message):
    config = message['path'].strip('/').split('/')
    label = config[0]
    Group('htv-' + label).add(message.reply_channel)
    topic = Topic(query=label)
    topic.frequency = config[1] if len(config) > 1 else 5
    topic.save()
    message.channel_session['query'] = label
    message.channel_session['topic_pk'] = topic.pk
    logger.debug("Conectado. Nuevo topic: %s" % label)


@channel_session
def ws_receive(message):
    topic = message.channel_session["topic_pk"]
    if not topic:
        return
    topic = Topic.objects.get(pk=topic)
    tw = TwitterAPI()
    last_id = 1
    count = 100
    tweets = tw.search(topic, last_id, count)
    logger.debug("Primera búsqueda, %s tweets" % len(tweets))
    count = 20
    next_tweet = Tweet()
    while True:
        for tweet in tweets:
            last_id = tweet.twitter_id
            logger.debug("Enviando tweet ID: %s" % (tweet.twitter_id))
            # mandar tweets
            Group('htv-' + topic.query).send({'text': json.dumps(tweet.as_json())})
            tweet.show()
            next_tweet = tweet
            logger.debug("Durmiendo %s segundos" % topic.frequency)
            sleep(topic.frequency)
        next_tweet = Tweet.objects.exclude(pk=next_tweet.pk).filter(topic=topic).order_by('last_shown', 'created_at')[:1].get()
        if next_tweet:
            logger.debug("Repitiendo tweet ID %s" % next_tweet.twitter_id)
            Group('htv-' + topic.query).send({'text': json.dumps(next_tweet.as_json())})
            next_tweet.show()
        tweets = tw.search(topic, last_id, count)
        logger.debug("Búscando nuevamente. %s tweets nuevos" % len(tweets))
        sleep(topic.frequency)


@channel_session
def ws_disconnect(message):
    logger.debug("Se desconectó el cliente.")
    Group('htv' + message.channel_session['query']).discard(message.reply_channel)