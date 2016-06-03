import json
import logging
from random import randint
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
    if config[0] == 'search':
        del config[0]
    label = config[0]
    group = 'htv-' + label + str(randint(100,999))
    Group(group).add(message.reply_channel)
    message.channel_session['groupname'] = group
    # creo un Topic
    topic = Topic(query=label)
    topic.frequency = config[1] if len(config) > 1 else 5
    topic.save()
    # almaceno en sesión datos que necesitaré luego
    message.channel_session['last_id'] = 1
    message.channel_session['topic_pk'] = topic.pk
    message.channel_session["first"] = True
    logger.debug("Conectado. Nuevo topic: %s" % label)


@channel_session
def ws_receive(message):
    if "topic_pk" not in message.channel_session.keys():
        Group(message.channel_session['groupname']).send({'text': json.dumps({'retry': True})})
        return
    topic = Topic.objects.get(pk=message.channel_session["topic_pk"])
    tw = TwitterAPI()
    data = json.loads(message['text'])
    # búscamos nuevos tweets
    if message.channel_session["first"]:
        logger.debug("Primera búsqueda, 30 tweets")
        tweets = tw.search(topic, message.channel_session['last_id'], 30)
        message.channel_session['last_id'] = tweets[len(tweets)-1].twitter_id if tweets else 1
        message.channel_session["first"] = False
    else:
        tweets = tw.search(topic, message.channel_session['last_id'], data['count'])
    for tweet in tweets[:10]:
        if tweet.twitter_id > message.channel_session['last_id']:
            message.channel_session['last_id'] = tweet.twitter_id
        logger.debug("Enviando tweet ID: %s" % (tweet.twitter_id))
        # mandar tweets
        sleep(topic.frequency)
        Group(message.channel_session['groupname']).send({'text': json.dumps(tweet.as_json())})
        tweet.show()
        logger.debug("Durmiendo %s segundos" % topic.frequency)

    if len(tweets) < data['count']:  # si no hay tweet nuevos, repetir pero buscando los mostrados hace más tiempo
        diff = data['count'] - len(tweets)
        for tweet_ret in Tweet.objects.filter(topic=topic).order_by('last_shown', 'created_at')[:diff]:
            logger.debug("Repitiendo tweet ID %s" % tweet_ret.twitter_id)
            sleep(topic.frequency)
            Group(message.channel_session['groupname']).send({'text': json.dumps(tweet_ret.as_json())})
            tweet_ret.show()


@channel_session
def ws_disconnect(message):
    logger.debug("Se desconectó el cliente.")
    Group(message.channel_session['groupname']).discard(message.reply_channel)
