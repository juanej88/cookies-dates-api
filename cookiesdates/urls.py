from django.contrib import admin
from django.urls import path, include
# from dj_rest_auth.registration.views import VerifyEmailView, ResendEmailVerificationView

urlpatterns = [
	path('', include('cookiesdatesdrf.urls')),
	path('admin/', admin.site.urls),
]
