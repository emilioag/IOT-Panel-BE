"""iotbe URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from iotbe.views import measures_between

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/mesures/(?P<name>\w{0,300})/from/(?P<from_timestamp>[0-9]+)/to/(?P<to_timestamp>[0-9]+)/by/(?P<interval>\w{0,300})', measures_between),
    url(
        r'^api-auth/',
        include('rest_framework.urls', namespace='rest_framework'))
]