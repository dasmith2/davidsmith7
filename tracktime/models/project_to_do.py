from django.db import models
from django.dispatch import receiver
from djaveClassMagic.signals import destroy_user

from tracktime.models.project import Project
from tracktime.models.to_do import ToDo, ToDoManager


@receiver(destroy_user, sender=Project)
def destroy_user_project_to_dos(sender, destroy_object=None, **kwargs):
  for project_to_do in destroy_object.projecttodo_set.all():
    project_to_do.destroy()


class ProjectToDoManager(ToDoManager):
  def select_related_list(self):
    return super().select_related_list() + ['project']

  def filter_project(self, qs, project):
    return qs.filter(project=project)


class ProjectToDo(ToDo):
  project = models.ForeignKey(
      Project, on_delete=models.PROTECT, help_text=(
          'What Project does this ProjectToDo apply to?'))

  @classmethod
  def model_description(cls):
    return """
        A ProjectToDo is a single task that a user intends to complete.
        Picking these is a bit of an art form. Ideally, you click "Done" on a
        few ProjectToDos every ProjectWorkSession. Then when you Report, you
        can see a steady rhythm. """

  live = ProjectToDoManager()
