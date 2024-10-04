from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Event

class CustomUserAdmin(UserAdmin):
  model = User
  list_display = ('username', 'email', 'first_name', 'last_name', 'timezone_offset', 'is_staff')
  fieldsets = UserAdmin.fieldsets + (
    (None, {'fields': ('timezone_offset', 'last_notification_date',)}),
  )

admin.site.register(User, CustomUserAdmin)
admin.site.register(Event)