from django.views.generic import TemplateView


class BaseTemplateView(TemplateView):
    template_name = 'account.html'
