from django.conf.urls import url, include
from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from users import views
from rest_framework.authtoken.views import ObtainAuthToken

urlpatterns = [ 
    url(r'^api/profile$', views.userList),
    url(r'^api/profile/pk$', views.userpk),
    url(r'^api/profile/add$', views.registerUser),
    url(r'^api/login$', views.login_user),
    url(r'api/image', views.image.as_view()),
    url(r'^api/profile/(?P<pk>[0-9]+)$', views.userDetail),    
    url(r'^auth/',ObtainAuthToken.as_view())
]


if settings.DEBUG:
    urlpatterns += static(settings.CODES_URL, document_root=settings.CODES_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)