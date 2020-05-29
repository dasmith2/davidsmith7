from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from tracktime.models.project import Project
from tracktime.models.to_do import ToDo, ToDoManager


@receiver(post_save, sender=ToDo)
def to_do_post_save(sender, instance, **kwargs):
  existing = ProjectToDo.all.filter(pk=instance.pk).first()
  if not existing:
    existing = ProjectToDo(todo_ptr=instance)
    existing.__dict__.update(instance.__dict__)
  existing.project_new = instance.project
  existing.save()


class ProjectToDoManager(ToDoManager):
  def select_related_list(self):
    return super().select_related_list() + ['project_new']

  def not_done(self, creator, project=None):
    filtered = super().not_done(creator)
    if project:
      filtered = filtered.filter(project=project)
    return filtered


class ProjectToDo(ToDo):
  project_new = models.ForeignKey(
      Project, on_delete=models.PROTECT, help_text=(
          'What project does this ToDo apply to?'))

  @classmethod
  def model_description(cls):
    return """
        A ProjectToDo is a single task that a user intends to complete. '
        Picking these is a bit of an art form. Ideally, you click "Done" on a
        few ProjectToDos every ProjectWorkSession. Then when you Report, you
        can see a steady rhythm. """

  live = ProjectToDoManager()
