from django.db import models

from tracktime.models.project import Project
from tracktime.models.to_do import ToDo, ToDoManager


class ProjectToDoManager(ToDoManager):
  def select_related_list(self):
    return super().select_related_list() + ['project_new']

  def not_done(self, creator, project=None):
    filtered = super().not_done(creator)
    if project:
      filtered = filtered.filter(project_new=project)
    return filtered


class ProjectToDo(ToDo):
  project_new = models.ForeignKey(
      Project, on_delete=models.PROTECT, help_text=(
          'What Project does this ProjectToDo apply to?'))

  @classmethod
  def model_description(cls):
    return """
        A ProjectToDo is a single task that a user intends to complete. '
        Picking these is a bit of an art form. Ideally, you click "Done" on a
        few ProjectToDos every ProjectWorkSession. Then when you Report, you
        can see a steady rhythm. """

  live = ProjectToDoManager()
