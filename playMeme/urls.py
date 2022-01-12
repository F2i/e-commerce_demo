from django.urls import path
from django.urls.resolvers import URLPattern
from . import views

urlpatterns = [
    path('fuck/', views.HelloView.as_view())
]