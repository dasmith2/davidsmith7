from django.contrib import admin

from tracktime.models.project import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
  list_display = ('name',)
