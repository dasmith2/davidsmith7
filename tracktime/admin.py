from django.contrib import admin

from tracktime.models import Project, WorkType


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
  list_display = ('name',)


@admin.register(WorkType)
class WorkTypeAdmin(admin.ModelAdmin):
  list_display = ('name',)
