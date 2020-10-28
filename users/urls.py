from django.conf.urls import url 
from django.conf import settings
from django.conf.urls.static import static
from users import views

urlpatterns = [ 
    url(r'^api/profile$', views.userList),
    url(r'^api/profile/add$', views.registerUser),
    url(r'^api/login$', views.login_user),
    url(r'^api/profile/(?P<pk>[0-9]+)$', views.userDetail),
    # url(r'api/image', views.image.as_view()),
    url(r'api/compile', views.compile),
    url(r'api/file', views.file),
    url(r'api/display', views.display),
]


if settings.DEBUG:
    urlpatterns += static(settings.CODES_URL, document_root=settings.CODES_ROOT)