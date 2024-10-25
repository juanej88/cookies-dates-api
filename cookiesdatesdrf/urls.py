from django.urls import path
from . import views

urlpatterns = [
  path('', views.Home.as_view(), name='home'),
  path('events/', views.EventListCreateView.as_view(), name='event-list-create'),
  path('events/<int:pk>', views.EventDetailView.as_view(), name='event-detail'),
  path('api/google-login/', views.GoogleLoginView.as_view(), name='google_login'),
  path('send-emails/', views.SendEmailsView.as_view(), name='send-emails'),
  path('reset-messages-left/', views.ResetMessagesLeftView.as_view(), name='reset-messages-left'),
  path('create-chatgpt-message/<int:pk>', views.CreateChatgptMessageView.as_view(), name='create-chatgpt-message'),
]
