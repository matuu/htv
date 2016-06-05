import json
from django.http import HttpResponse
from django.views.generic import TemplateView

from twitter_app.api import TwitterAPI
from twitter_app.models import Topic, Tweet


class IndexView(TemplateView):
    template_name = "frontend/index.html"


class TopicView(TemplateView):
    template_name = "frontend/results.html"


class SearchTweetJsonResponse(TemplateView):

    def get(self, request, **kwargs):
        search = self.kwargs.get("key", '')
        topic = Topic(query=search, frequency=10)
        tw = TwitterAPI()
        tweets = tw.search(topic, since_id=0, save=False)
        jsons = [tweet.as_json() for tweet in tweets]

        return HttpResponse( json.dumps({
            'data': jsons
        }), content_type='application/json')


index = IndexView.as_view()
results = TopicView.as_view()
json_results = SearchTweetJsonResponse.as_view()