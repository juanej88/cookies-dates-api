from typing import Any, Optional
from django.core.management.base import BaseCommand
from cookiesdatesdrf.tasks import send_event_notification_emails

class Command(BaseCommand):
  help = 'Send event notification emails to users'

  def handle(self, *args, **options):
    response = send_event_notification_emails()
    self.stdout.write(self.style.SUCCESS(response))