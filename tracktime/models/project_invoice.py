from django.db import models
from django.dispatch import receiver
from django.shortcuts import reverse
from djaveClassMagic.signals import destroy_user

from invoice.models.invoice import Invoice, LiveInvoiceManager
from tracktime.models.project import Project


@receiver(destroy_user, sender=Project)
def destroy_user_project_line_items(sender, destroy_object=None, **kwargs):
  for project_invoice in destroy_object.projectinvoice_set.all():
    destroy_user.send(sender=ProjectInvoice, destroy_object=project_invoice)
    destroy_user.send(sender=Invoice, destroy_object=project_invoice)
    project_invoice.destroy()


class LiveProjectInvoiceManager(LiveInvoiceManager):
  def get_invoices(
      self, user, created_from, created_to, project, status, nnow=None):
    qs = super().get_invoices(
        user, created_from, created_to, status, nnow=nnow)
    if project:
      project_id = project
      if isinstance(project, Project):
        project_id = project.pk
      qs = qs.filter(project_id=project_id)
    return qs


class ProjectInvoice(Invoice):
  project = models.ForeignKey(Project, on_delete=models.PROTECT, help_text=(
      'What Project is this Invoice collecting payment for?'))

  @classmethod
  def filter_allowed_by_user(cls, user, query_set):
    return super().filter_allowed_by_user(
        user, query_set).select_related('project')

  @classmethod
  def model_description(cls):
    return (
        'A ProjectInvoice is an Invoice for time tracked against a Project. '
        'A ProjectInvoice is made up of ProjectLineItems and ManualLineItems.')

  def select_related_list(self):
    return super().select_related_list() + ['project']

  def add_to_json(self, existing_json):
    super().add_to_json(existing_json)
    existing_json['project_name'] = self.project.name

  def view_url(self):
    return reverse('view_project_invoice', kwargs={'pk': self.pk})

  live = LiveProjectInvoiceManager()
