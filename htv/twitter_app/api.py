import twitter

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from .models import Tweet


class TwitterAPI(object):
    """
    mínimo uso de la api de twitter a través de python-twitter.
    """
    def __init__(self):
        if not all([settings.CONSUMER_KEY, settings.CONSUMER_SECRET,
                    settings.ACCESS_TOKEN_KEY, settings.ACCESS_TOKEN_SECRET, ]):
            raise ImproperlyConfigured("Debe definir los token de acceso a la API de twitter")

        self.api = twitter.Api(settings.CONSUMER_KEY, settings.CONSUMER_SECRET,
                               settings.ACCESS_TOKEN_KEY, settings.ACCESS_TOKEN_SECRET)

    def search(self, topic, since_id=None, count=10):
        if since_id:
            tweets = self.api.GetSearch(topic.query, since_id=since_id, count=count, result_type='recent')
        else:
            tweets = self.api.GetSearch(topic.query, count=count, result_type='recent')
        tweets_insert = []
        for tweet in tweets:
            aux = Tweet.from_twitter(tweet, topic)
            if aux:
                tweets_insert.append(aux)
        # guardamos todos los tweets
        Tweet.objects.bulk_create(tweets_insert, batch_size=30)
        tweets_insert.sort(key=lambda x: x.created_at)
        return tweets_insert
