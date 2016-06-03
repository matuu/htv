import json
from datetime import datetime

from django.core import serializers
from django.db import models
from django.utils import timezone


class Topic(models.Model):
    search_at = models.DateTimeField(auto_now_add=True)
    query = models.CharField(max_length=255)
    frequency = models.PositiveSmallIntegerField(default=5)


class Tweet(models.Model):
    twitter_id = models.IntegerField()
    topic = models.ForeignKey(Topic)
    user_name = models.CharField(max_length=255)
    user_screenname = models.CharField(max_length=255)
    user_location = models.CharField(max_length=255, null=True, blank=True)
    user_profile_image_url = models.CharField(max_length=255)
    text = models.CharField(max_length=255)
    created_at = models.DateTimeField()
    retweet_count = models.PositiveIntegerField(default=0)
    media_url = models.CharField(max_length=255, blank=True, null=True)

    # control
    is_shown = models.BooleanField(default=False)
    last_shown = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "{}: {}".format(self.user_screenname, self.text)

    @staticmethod
    def from_twitter(obj, topic_rel):
        # primero chequeamos que no exista ya el tweets dentro del topic usado
        if Tweet.objects.filter(topic_id=topic_rel.pk, twitter_id=obj.id).exists():
            return None
        t = Tweet()
        t.topic = topic_rel
        t.twitter_id = obj.id
        t.user_name = obj.user.name
        t.user_screenname = obj.user.screen_name
        t.user_location = None if not obj.user.location else obj.user.location
        t.user_profile_image_url = obj.user.profile_image_url
        t.text = obj.text
        t.created_at = datetime.strptime(obj.created_at, '%a %b %d %H:%M:%S %z %Y')
        t.retweet_count = obj.retweet_count if obj.retweet_count else 0
        if obj.media:
            t.media_url = obj.media[0].media_url_https
        return t

    def as_json(self):
        return json.loads(serializers.serialize('json', [self, ]))[0]["fields"]

    def show(self):
        self.is_shown = True
        self.last_shown = timezone.now()
        self.save()