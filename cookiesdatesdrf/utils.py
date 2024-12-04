from datetime import date, timedelta

import os
from openai import OpenAI
from dotenv import load_dotenv


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


def create_chatgpt_message(person_name, person_details=None, previous_message=None):
  load_dotenv()
  try:
    client = OpenAI()

    system_message = {
      'role': 'system',
      'content': 'You are an assistant that generates thoughtful and heartwarming birthday messages with a strict maximum of 60 tokens. When users provide personal details, incorporate them to make the message more unique and meaningful. If no specific details are provided, generate a generic but heartfelt birthday message. Avoid repeating previous messages. Avoid using their last names if given. If a user asks a question unrelated to birthday messages, politely inform them of your focus and invite them to ask about birthday messages.',
    }

    user_message_content = f"Birthday person's name is {person_name}."

    if person_details:
      user_message_content += f'Here are some personal details: {person_details}.'

    if previous_message:
      user_message_content += f'The previous message is: {previous_message}.'

    user_message = {
      'role': 'user',
      'content': user_message_content
    }
  
    response = client.chat.completions.create(
      model='gpt-4o-mini',
      messages=[system_message, user_message],
      max_completion_tokens=100,
    )

    return response.choices[0].message.content
  except Exception as error:
    return print(error)


if __name__ == '__main__':
  person_name = 'Tim'
  person_details = ''
  previous_message = ''
  response = create_chatgpt_message(person_name, person_details, previous_message)
  print(response)

  # print('Notification Date:', get_notification_date(date(1988,10,4), 1))