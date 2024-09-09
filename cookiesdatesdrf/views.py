from django.shortcuts import render
from django.http import HttpResponse

def home(request):
  if request.user.is_authenticated:
    return HttpResponse('Cookies & Dates, Welcome Home', {})
  return HttpResponse('Cookies & Dates, You must log in', {})