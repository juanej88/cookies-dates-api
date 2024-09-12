from django.contrib import admin
from django.urls import path, include
from dj_rest_auth.registration.views import VerifyEmailView, ResendEmailVerificationView

urlpatterns = [
	path('', include('cookiesdatesdrf.urls')),
  path('api/auth/', include('dj_rest_auth.urls')),
  path('api/auth/registration/', include('dj_rest_auth.registration.urls')),
  path('api/auth/account-confirm-email/', VerifyEmailView.as_view(), name='account_email_verification_sent'),
  path('api/auth/account-confirm-email/<str:key>/', VerifyEmailView.as_view(), name='account_confirm_email'),
  path('api/auth/resend-email/', ResendEmailVerificationView.as_view(), name="rest_resend_email"),
	path('admin/', admin.site.urls),
]
