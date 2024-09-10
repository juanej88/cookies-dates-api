from django.shortcuts import render
from django.http import HttpResponse

def home(request):
  if request.user.is_authenticated:
    return HttpResponse(f'Cookies & Dates, Welcome Home {request.user.email}', {})
  return HttpResponse('Cookies & Dates, You must log in', {})