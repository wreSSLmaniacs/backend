from django.conf.urls import url, include
from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from projects import views
from rest_framework.authtoken.views import ObtainAuthToken

urlpatterns = [ 
    url(r'api/compile/(?P<username>[a-zA-Z0-9]+)/(?P<dirk>[a-zA-Z0-9\/\_]*)$', views.compile),   
    url(r'api/display/(?P<username>[a-zA-Z0-9]+)/(?P<dirk>[a-zA-Z0-9\/\_]*)$', views.displayAll),
    url(r'api/display/(?P<username>[a-zA-Z0-9]+)/(?P<dirk>[a-zA-Z0-9\/\_]*)/(?P<file>[a-zA-Z0-9\_]+\.[a-zA-Z0-9\_]+)$', views.display),
    url(r'api/rename/(?P<username>[a-zA-Z0-9]+)/(?P<dirk>[a-zA-Z0-9\/\_]*)$', views.rename),
]