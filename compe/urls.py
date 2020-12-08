from django.conf.urls import url, include
from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from compe.views import newcontest, getcontest, runcode, runfile, runboard, upboard, pastboard, getpoints, isrunning, passedpoints
from rest_framework.authtoken.views import ObtainAuthToken

urlpatterns = [ 
    url(r'api/contest/get/running', runboard),
    url(r'api/contest/get/upcoming', upboard),
    url(r'api/contest/get/past', pastboard),
    url(r'api/contest/postcontest', newcontest),
    url(r'api/competition/(?P<id>[0-9]+)$', getcontest),
    url(r'api/submit/code/(?P<id>[0-9]+)$', runcode),
    url(r'api/submit/file/(?P<id>[0-9]+)$', runfile),
    url(r'api/points/(?P<user>[a-zA-Z0-9]+)$', getpoints),
    url(r'api/contest/isrunning/(?P<id>[0-9]+)$', isrunning),
    url(r'api/contest/passed/(?P<id>[0-9]+)/(?P<user>[a-zA-Z0-9]+)$', passedpoints),
]