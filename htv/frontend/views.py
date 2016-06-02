from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = "frontend/index.html"


class TopicView(TemplateView):
    template_name = "frontend/results.html"


index = IndexView.as_view()
results = TopicView.as_view()