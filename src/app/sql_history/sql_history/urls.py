# -*- coding: utf-8 -*-
"""sql_history URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from search_result import views as result_views
from django.conf import settings
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^$', result_views.home, name='home'),
    url(r'^home_page/$', result_views.home_page, name='home_page'),
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/login/$', result_views.login, name='login'),
    url(r'^accounts/logout/$', result_views.logout, name='logout'),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_PATH}),
    url(r'^table_SQL_history/', result_views.home, name='sql_history'),
    url(r'^date_static/', result_views.date_static, name='date_static'),
    url(r'^(?P<user>\w+)/$', result_views.user_detail, name='user_detail'),
    url(r'^(?P<date>\d+-\d+-\d+)&(?P<user>\w+)/$', result_views.user_date, name='user_date'),
    url(r'^(?P<date>\d+-\d+-\d+)/$', result_views.date_detail, name='date_detail'),
    url(r'^home/fofeasy', result_views.fofeasy_home, name='fofeasy_home'),
    url(r'^(?P<user_id>\w+)/fofeasy$', result_views.fofeasy_user_detail, name='fofeasy_user_detail'),
    url(r'^(?P<date>\d+-\d+-\d+)/fofeasy$', result_views.fofeasy_date_detail, name='fofeasy_date_detail'),
    url(r'^(?P<date>\d+-\d+-\d+)&(?P<user_id>\w+)/fofeasy$', result_views.fofeasy_user_date_detail,
        name='fofeasy_user_date_detail'),
]
