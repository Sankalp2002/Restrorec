from django.conf.urls import url
from django.urls.resolvers import URLPattern
from . import views
from django.urls import path
from django.contrib import admin
app_name = 'Reco'
urlpatterns = [
    path('', views.showRest, name='showRest'),
    path('menu', views.showMenu, name='showMenu'),
    path('register', views.registerView, name='registerView'),
    path('login', views.loginView, name='loginView'),
]
