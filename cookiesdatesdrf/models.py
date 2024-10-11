from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from .utils import get_notification_date


class User(AbstractUser):
  timezone_offset = models.IntegerField(default=0)
  last_notification_date = models.DateField(null=True, blank=True)

  def get_local_time(self):
    return timezone.now() - timedelta(minutes=self.timezone_offset)


class Event(models.Model):
  name = models.CharField(max_length=25)
  date = models.DateField()
  full_date = models.BooleanField(default=True)
  event_type = models.CharField(max_length=15)
  notify = models.BooleanField(default=False)
  notification_days = models.PositiveSmallIntegerField(
    validators=[MinValueValidator(0), MaxValueValidator(30)],
    default=0
  )
  notification_date = models.DateField(null=True, blank=True)
  previous_message = models.CharField(max_length=250, null=True, blank=True)
  
  user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='events')

  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  def __str__(self) -> str:
    return f'{self.user.email}: {self.name}'
  
  def save(self, *args, **kwargs):
    if self.notify:
      self.notification_date = get_notification_date(self.date, self.notification_days)
    else: 
      self.notification_date = None
    super().save(*args, **kwargs)