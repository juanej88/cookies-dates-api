from django.core.mail import send_mail
from django.template.loader import render_to_string
from .models import User, Event

def send_event_notification_emails():
  for user in User.objects.all():
    user_local_time = user.get_local_time()
    user_local_date = user_local_time.date()

    # Check if it is 8am in the user's local time and if they have not received any notifications today
    if (user.last_notification_date is None or user.last_notification_date < user_local_date) and user_local_time.hour >= 6:
      today_events = Event.objects.filter(
        user=user,
        notify=True,
        notification_date=user_local_date
      ).order_by('notification_days')

      if today_events.exists():
        # Email content to be passed to the email template
        context = {
          'user': user,
          'events': today_events,
          'date': user_local_date,
        }
        
        email_body = render_to_string('email/event_notification.html', context)
        subject = 'You Have 1 Notification for Today' if len(today_events) == 1 else f'You Have {len(today_events)} Notifications for Today'
        from_email = 'Cookies & Dates'
        recipient_list = [user.email]

        send_mail(subject, email_body, from_email, recipient_list, html_message=email_body)

        # Update user's last notification date
        user.last_notification_date = user_local_date
        user.save()

  return 'Event notification emails sent successfully'