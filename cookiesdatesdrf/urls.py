from django.urls import path
from . import views

urlpatterns = [
  path('', views.home, name='home'),
  path('api/google-login/', views.GoogleLoginView.as_view(), name='google_login'),
]
