from rest_framework import serializers
from .models import Event

class EventSerializer(serializers.ModelSerializer):
  user = serializers.ReadOnlyField(source='user.email')
  class Meta:
    model = Event
    fields = ['id', 'name', 'date', 'full_date', 'event_type', 'notify', 'notification_days', 'user']