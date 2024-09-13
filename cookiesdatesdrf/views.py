from django.shortcuts import render
from django.http import HttpResponse
# Get CLIENT_ID from dotenv to log in with google
import os
from dotenv import load_dotenv
load_dotenv()
# Log in with google
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from google.oauth2 import id_token
from google.auth.transport import requests

def home(request):
  if request.user.is_authenticated:
    return HttpResponse(f'Cookies & Dates, Welcome Home {request.user.email}', {})
  return HttpResponse('Cookies & Dates, You must log in', {})

User = get_user_model()

class GoogleLoginView(APIView):
  def post(self, request):
    token = request.data.get('token')
      
    try:
      CLIENT_ID = os.environ.get('CLIENT_ID')
      
      # Verify the token
      idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)

      # Get user info from the decoded token
      # userid = idinfo['sub']
      email = idinfo['email']
      first_name = idinfo.get('given_name')
      last_name = idinfo.get('family_name')
      
      # Check if the email is verified
      if idinfo['email_verified']:
        # Check if user exists, if not create a new one
        user, created = User.objects.get_or_create(
          email=email,
          defaults={
            'username': email,
            'first_name': first_name,
            'last_name': last_name,
          }
        )

        # Generate or get the token
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