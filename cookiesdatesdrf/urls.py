from django.urls import path
from . import views

urlpatterns = [
  path('', views.Home.as_view(), name='home'),
  path('api/google-login/', views.GoogleLoginView.as_view(), name='google_login'),
]
