
from django.conf.urls import url
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from users import views
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token

urlpatterns = [ 
    url(r'^api/profile$', views.userList),
    url(r'^api/profile/add$', views.registerUser),
    url(r'^api/login$', views.login_user),
    url(r'^api/profile/(?P<pk>[0-9]+)$', views.userDetail),
    url(r'api/compile', views.compile),
    
    # JWT
    path('auth/', include('rest_auth.urls')),
    path('auth/signup/', include('rest_auth.registration.urls')),
    path('auth/refresh-token/', refresh_jwt_token),
    
    url(r'api/display/(?P<username>[a-zA-Z0-9]+)/(?P<dirk>[a-zA-Z0-9\/\_]*)$', views.displayAll),
    url(r'api/display/(?P<username>[a-zA-Z0-9]+)/(?P<dirk>[a-zA-Z0-9\/\_]*)/(?P<file>[a-zA-Z0-9\_]+\.[a-zA-Z0-9\_]+)$', views.display)
]


if settings.DEBUG:
    urlpatterns += static(settings.CODES_URL, document_root=settings.CODES_ROOT)