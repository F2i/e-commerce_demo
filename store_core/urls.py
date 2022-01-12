from django.urls import path
from django.urls.resolvers import URLPattern
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='store_core/index.html'))
]