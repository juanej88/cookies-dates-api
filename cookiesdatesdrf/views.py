from rest_framework.permissions import IsAuthenticated

# Log in with google
from django.contrib.auth import get_user_model
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

class Home(APIView):
  permission_classes = [IsAuthenticated]

  def get(self, request):
    return Response({'message': 'Welcome to Cookies & Dates'})

User = get_user_model()

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

        # Generate or get a token
        token, _ = Token.objects.get_or_create(user=user)

        response = Response({
          'message': 'Login successful',
          'user_id': user.id,
          'email': user.email,
          'first_name': user.first_name,
          'last_name': user.last_name,
        }, status=status.HTTP_200_OK)

        response.set_cookie(
          'auth_token',
          token.key,
          httponly=True,  # Prevents JavaScript access
          # secure=True,    # Sends only over HTTPS
          samesite='Lax', # Provides CSRF protection
          max_age=2592000,   # Expires in 30 days
        )

        return response
      else:
        return Response({'error': 'Email not verified'}, status=status.HTTP_400_BAD_REQUEST)
    
    except ValueError:
      # Invalid token
      return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)