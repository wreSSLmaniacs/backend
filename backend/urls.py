"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import include, url
from compe.views import newcontest, getcontest, runcode, runfile, runboard, upboard, pastboard, getpoints

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'api/contest/get/running', runboard),
    url(r'api/contest/get/upcoming', upboard),
    url(r'api/contest/get/past', pastboard),
    url(r'api/contest/postcontest', newcontest),
    url(r'api/competition/(?P<id>[0-9]+)$', getcontest),
    url(r'api/submit/code/(?P<id>[0-9]+)$', runcode),
    url(r'api/submit/file/(?P<id>[0-9]+)$', runfile),
    url(r'api/points/(?P<user>[a-zA-Z0-9]+)$', getpoints),
    url(r'^', include('users.urls')),
]
