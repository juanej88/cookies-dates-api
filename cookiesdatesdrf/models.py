from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from .utils import get_notification_date

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
  
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')

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