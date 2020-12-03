from django.conf.urls import url
from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from users import views

from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token

urlpatterns = [ 
    url(r'^api/profile$', views.userList),
    url(r'^api/profile/add$', views.registerUser),
    url(r'^api/login$', views.login_user),
    url(r'^api/profile/(?P<pk>[0-9]+)$', views.userDetail),
    url(r'api/compile', views.compile),
    url(r'api/file', views.file),
    url(r'api/display', views.display),
    
    # path(r'api-token-auth/', obtain_jwt_token),
    # path(r'api-token-refresh/', refresh_jwt_token),
]


if settings.DEBUG:
    urlpatterns += static(settings.CODES_URL, document_root=settings.CODES_ROOT)