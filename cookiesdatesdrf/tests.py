from django.test import TestCase
from unittest.mock import patch
from django.utils import timezone
from datetime import timedelta
import os
from .models import User, Event
from .tasks import send_event_notification_emails, reset_messages_left

class SendEventNotificationEmailsTest(TestCase):
  def setUp(self):
    # Set the Testing environment variable to prevent notification_date update in tests
    os.environ['TESTING'] = 'True'

    # Create a test user
    self.user = User.objects.create(
      first_name='testuser',
      username='testuser@example.com',
      email='testuser@example.com',
      timezone_offset=-480, # Perth time
      last_notification_date=timezone.now().date() - timedelta(days=1),
    )

    # Create a test event that triggers a notification
    self.event = Event.objects.create(
      user=self.user,
      name='John Smith',
      date=timezone.now().date(),
      event_type='birthday',
      notify=True,
      notification_days=0,
      notification_date=timezone.now().date(),
    )

  @patch('cookiesdatesdrf.tasks.send_mail')
  def test_send_event_notification_emails(self, mock_send_mail):
    response = send_event_notification_emails()

    # Assertions to ensure the email was sent
    self.assertEqual(response, 'Event notification emails sent successfully: 1 email(s) sent.')
    mock_send_mail.assert_called_once()

    # Get the arguments passed to send_mail
    call_args = mock_send_mail.call_args_list[0][0]
    subject = call_args[0]
    email_body = call_args[1]
    recipient_list = call_args[3]

    # Verify the email content
    self.assertIn('You Have 1 Notification for Today', subject)
    self.assertIn(self.user.email, recipient_list)
    self.assertIn(self.user.first_name, email_body)

    # Verify that the user's last_notification_date was updated
    self.user.refresh_from_db()
    self.assertEqual(self.user.last_notification_date, timezone.now().date())

  @patch('cookiesdatesdrf.tasks.send_mail')
  def test_no_notification_sent_if_already_notified(self, mock_send_mail):
    # Update the user's last_notification_date to today
    self.user.last_notification_date = timezone.now().date()
    self.user.save()

    response = send_event_notification_emails()

    # Ensure no email is sent
    mock_send_mail.assert_not_called()
    # Verify the response
    self.assertEqual(response, 'No emails were sent as there were no notifications to send.')


class ResetMessageLeftTest(TestCase):
  def setUp(self):
    # Create some test users
    User.objects.create(username='testuser1', messages_left=7)
    User.objects.create(username='testuser2', messages_left=4)
  
  def test_reset_messages_left_success(self):
    response = reset_messages_left()

    self.assertEqual(response, 'Messages left successfully reset for all users')

    # Check if messages_left is reset to 10 for all users
    users = User.objects.all()
    for user in users:
      self.assertEqual(user.messages_left, 10)    