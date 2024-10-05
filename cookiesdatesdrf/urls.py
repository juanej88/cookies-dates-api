from django.urls import path
from . import views

urlpatterns = [
  path('', views.Home.as_view(), name='home'),
  path('events/', views.EventListCreateView.as_view(), name='event-list-create'),
  path('events/<int:pk>', views.EventDetailView.as_view(), name='event-detail'),
  path('api/google-login/', views.GoogleLoginView.as_view(), name='google_login'),
  path('test-email', views.TestEmail.as_view(), name='test-email'),
]
