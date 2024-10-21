# Event Views
from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

# GoogleLoginView
import requests
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

# ChatGPT View
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework.exceptions import PermissionDenied

# Send Emails View
import os
from dotenv import load_dotenv

from .serializers import EventSerializer
from .models import Event

from .utils import test_email, create_chatgpt_message
from .tasks import send_event_notification_emails


class Home(APIView):
  authentication_classes = [TokenAuthentication]
  permission_classes = [IsAuthenticated]

  def get(self, request):
    return Response({'message': 'Welcome to Cookies & Dates'})


class TestEmail(APIView):
  def get(self, request):
    test_email()
    return Response({'message': 'Email Sent Successfully!'})


class EventListCreateView(generics.ListCreateAPIView):
  serializer_class = EventSerializer
  authentication_classes = [TokenAuthentication]
  permission_classes = [IsAuthenticated]
  
  def get_queryset(self):
    return Event.objects.filter(user=self.request.user)
  
  def perform_create(self, serializer):
    serializer.save(user=self.request.user)


class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
  serializer_class = EventSerializer
  authentication_classes = [TokenAuthentication]
  permission_classes = [IsAuthenticated]

  def get_queryset(self):
    return Event.objects.filter(user=self.request.user)

  def perform_update(self, serializer):
    serializer.save(user=self.request.user)

  def perform_destroy(self, instance):
    instance.delete()


class GoogleLoginView(APIView):
  def post(self, request):
    token = request.data.get('token')

    if not token:
      return Response({'error': 'Access token is required'}, status=status.HTTP_400_BAD_REQUEST)
      
    try:
      # Make a request to Google's UserInfo endpoint
      user_info_url = 'https://www.googleapis.com/oauth2/v3/userinfo'
      headers = {'Authorization': f'Bearer {token}'}
      response = requests.get(user_info_url, headers=headers)
      user_info = response.json()
      
      email = user_info['email']
      first_name = user_info.get('given_name')
      last_name = user_info.get('family_name')
      
      # Check if the email is verified
      if user_info['email_verified']:
        # Check if user exists, if not create a new one
        User = get_user_model()
        user, created = User.objects.get_or_create(
          email=email,
          defaults={
            'username': email,
            'first_name': first_name,
            'last_name': last_name,
          }
        )

        timezone_offset = request.data.get('timezoneOffset', 0)
        user.timezone_offset = int(timezone_offset)
        user.save()

        # Generate or get a token
        token, _ = Token.objects.get_or_create(user=user)

        return Response({
          'message': 'Login successful',
          'user_id': user.id,
          'email': user.email,
          'first_name': user.first_name,
          'last_name': user.last_name,
          'messages_left': user.messages_left,
          'token': token.key,
        }, status=status.HTTP_200_OK)
      else:
        return Response({'error': 'Email not verified'}, status=status.HTTP_400_BAD_REQUEST)
    
    except ValueError:
      # Invalid token
      return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


class SendEmailsView(APIView):
  def get(self, request, *args, **kwargs):
    load_dotenv()
    CRON_SECRET_TOKEN = os.environ.get('CRON_SECRET_TOKEN')
    auth_header = request.headers.get('Authorization')
    if auth_header != f'Bearer {CRON_SECRET_TOKEN}':
      return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
      send_event_notification_emails()
      return Response({'message': 'Emails sent successfully'}, status=status.HTTP_200_OK)
    except Exception as e:
      return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CreateChatgptMessageView(generics.UpdateAPIView):
  serializer_class = EventSerializer
  authentication_classes = [TokenAuthentication]
  permission_classes = [IsAuthenticated]

  def get_object(self):
    event_id = self.kwargs.get('pk')
    return get_object_or_404(Event, id=event_id, user=self.request.user)
  
  @transaction.atomic
  def update(self, request, *args, **kwargs):
    # Check messages_left
    User = get_user_model()
    user = User.objects.select_for_update().get(id=request.user.id)

    if user.messages_left <= 0:
      raise PermissionDenied('You have no messages left for this month.')

    event_instance = self.get_object()
    person_details = request.data.get('person_details', None)

    message = create_chatgpt_message(
      event_instance.name,
      person_details, 
      event_instance.previous_message
    )

    serializer = self.get_serializer(event_instance, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save(previous_message=message)

    # Update messages_left
    user.messages_left -= 1
    user.save()

    response_data = serializer.data
    response_data['messages_left'] = user.messages_left

    return Response(response_data)