"""api URL Configuration

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
from django.urls import path
from django.contrib import admin
from django.contrib import admin
from django.urls import path, include 
from webcam.views import video_feed_1
from picture.views import PictureViewSet,StatsticsViewSet
from rest_framework import routers

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from django.conf.urls import url

#from user.views import kakao_login, kakao_callback


urlpatterns = []
router = routers.SimpleRouter()

schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   validators=['flex', 'ssv'],
   public=True,
   permission_classes=(permissions.AllowAny,),
)

router.register(
    r'^v1/pictures',PictureViewSet,basename='picture'
)

router.register(
    r'^v1/statistics', StatsticsViewSet, basename='picture'
)


urlpatterns.extend([
    path('admin/', admin.site.urls),
    
    # kakao
#    path('account/login/kakao/', kakao_login, name='kakao_login'),
#    path('account/login/kakao/callback/', kakao_callback, name='kakao_callback'),

    # webcam
    path('video_feed_1/', video_feed_1, name="video-feed-1"),
    url(r'^doc/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
])
urlpatterns.extend(router.urls)
