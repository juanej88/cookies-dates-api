from datetime import date, timedelta

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


if __name__ == '__main__':
  print('Notification Date:', get_notification_date(date(1988,10,4), 1))