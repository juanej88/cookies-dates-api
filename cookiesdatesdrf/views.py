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

from .serializers import EventSerializer
from .models import Event

from .utils import test_email

class Home(APIView):
  authentication_classes = [TokenAuthentication]
  permission_classes = [IsAuthenticated]

  def get(self, request):
    return Response({'message': 'Welcome to Cookies & Dates'})

User = get_user_model()

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
          'token': token.key,
        }, status=status.HTTP_200_OK)
      else:
        return Response({'error': 'Email not verified'}, status=status.HTTP_400_BAD_REQUEST)
    
    except ValueError:
      # Invalid token
      return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)