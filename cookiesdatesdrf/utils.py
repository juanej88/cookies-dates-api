from datetime import date, timedelta
from django.core.mail import send_mail
from django.template.loader import render_to_string

def get_upcoming_event(event, today, this_year, next_year):
  month = event.month
  day = event.day
  upcoming_event = ''

  try:
    upcoming_event = date(this_year, month, day)
  except ValueError:
    upcoming_event = date(this_year, month, day - 1)

  if today > upcoming_event:
    try:
      upcoming_event = date(next_year, month, day)
    except ValueError:
      upcoming_event = date(next_year, month, day - 1)

  return upcoming_event


def get_notification_date(event, notification_days):
  today = date.today()
  this_year = today.year
  next_year = this_year + 1
  upcoming_event = get_upcoming_event(event, today, this_year, next_year)

  days = timedelta(days=notification_days)
  notification_date = upcoming_event - days

  if today >= notification_date:
    upcoming_event = get_upcoming_event(event, today, this_year + 1, next_year + 1)
    notification_date = upcoming_event - days

  return notification_date


def test_email():
  today = date(2024, 3, 3)
  events = [
    {
      'name': 'Veronika Olejárová',
      'event_type': 'birthday',
      'date': date(1992, 3, 3),
      'notification_days': 0,
    },
    {
      'name': 'Wedding Anniversary',
      'event_type': 'special',
      'date': date(2024, 2, 1),
      'notification_days': 14,
    },
  ]
  context = {
    'today': today,
    'user': {'first_name': 'Juan'},
    'events': events,
  }

  email_body = render_to_string('email/event_notification.html', context)
  
  subject = '[Cookies & Dates] Your Notifications for today'
  from_email = 'Cookies & Dates'
  recipient_list = ['arq.jorrin@gmail.com']

  send_mail(subject, email_body, from_email, recipient_list, html_message=email_body)


if __name__ == '__main__':
  # print('Notification Date:', get_notification_date(date(1988,10,4), 1))
  test_email()