from django.conf.urls import url
from django.urls.resolvers import URLPattern
from . import views
from django.urls import path
from django.contrib import admin
app_name = 'Reco'
urlpatterns = [
    path('', views.showMenus, name='showMenus')
]
