from django.contrib import admin

from djavError.models import Error, Notification, LongRequest


def mark_fixed(modeladmin, request, queryset):
  queryset.update(fixed=True)


mark_fixed.short_description = 'Mark fixed'


@admin.register(Error)
class DjavErrorAdmin(admin.ModelAdmin):
  list_display = (
      'title', 'fixed', 'latest', 'created', 'count', 'error_message',
      'to')
  ordering = ('-latest', '-created',)
  actions = [mark_fixed]


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
  list_display = ('title', 'created', 'latest', 'count', 'message', 'to')


@admin.register(LongRequest)
class LongRequestAdmin(admin.ModelAdmin):
  list_display = ('path', 'method', 'average_duration')
  ordering = ('-latest', '-created',)
