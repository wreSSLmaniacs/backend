
from django.conf.urls import url
from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from users import views

from rest_framework.authtoken.views import ObtainAuthToken

urlpatterns = [ 
    url(r'^api/profile$', views.userList),
    url(r'^api/profile/add$', views.registerUser),
    url(r'^api/login$', views.login_user),
    url(r'^api/profile/(?P<pk>[0-9]+)$', views.userDetail),
    url(r'api/compile', views.compile),
    url(r'api/display/(?P<username>[a-zA-Z0-9]+)$', views.displayAll),
    url(r'api/display/(?P<username>[a-zA-Z0-9]+)/(?P<file>[a-zA-Z0-9\.\_]+)$', views.display),
    path(r'api/auth', ObtainAuthToken.as_view()),
    # path(r'api/refresh', refresh_jwt_token),
]


if settings.DEBUG:
    urlpatterns += static(settings.CODES_URL, document_root=settings.CODES_ROOT)