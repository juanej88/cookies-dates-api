from rest_framework import serializers
from .models import User, Event

class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ['id', 'username', 'email', 'first_name', 'last_name', 'timezone_offset', 'last_notification_date']

class EventSerializer(serializers.ModelSerializer):
  user = serializers.ReadOnlyField(source='user.email')
  class Meta:
    model = Event
    fields = ['id', 'name', 'date', 'full_date', 'event_type', 'notify', 'notification_days', 'notification_date', 'user']