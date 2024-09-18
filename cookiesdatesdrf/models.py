from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

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
  
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')

  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  def __str__(self) -> str:
    return f'{self.user.email}: {self.name}'