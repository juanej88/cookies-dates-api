from django.contrib import admin
from django.urls import path, include

urlpatterns = [
	path('', include('cookiesdatesdrf.urls')),
  path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
  path('auth/', include('djoser.urls')),
	path('accounts/', include('allauth.urls')),
  path("_allauth/", include("allauth.headless.urls")),
	path('admin/', admin.site.urls),
]
