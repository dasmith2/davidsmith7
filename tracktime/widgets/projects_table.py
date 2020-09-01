from django.shortcuts import reverse
from djaveClassMagic.edit_list_table import EditListTable
from djaveHTML.button import Button
from djaveHTML.a import A
from djaveHTML.table import ButtonsCell

from tracktime.models.project import Project


class BaseProjectsTable(EditListTable):
  def __init__(self):
    super().__init__(Project, ['Name', ''])
    self.setup_edit_ajax('name')

  def create_row_for_existing(self, project, archive_action):
    archive_button = Button(archive_action)
    edit_button = A(
        'Edit', reverse('edit_project', kwargs={'pk': project.pk}),
        classes=['edit'], button=True)
    buttons_cell = ButtonsCell([edit_button, archive_button])
    self.create_row([project.name, buttons_cell], pk=project.pk)


class ProjectsTable(BaseProjectsTable):
  def __init__(self, user):
    self.user = user

    super().__init__()

    self.setup_existing()
    self.setup_click_updates_field(
        '.archive', 'deleted', "'now'", 'remove_row')
    self.append_create_new_row('Create new project', reverse('edit_project'))

  def setup_existing(self):
    for project in Project.live.allowed_by_user(self.user).order_by('name'):
      self.create_row_for_existing(project, 'Archive')


class ArchivedProjectsTable(BaseProjectsTable):
  def __init__(self, user):
    self.user = user
    super().__init__()
    self.setup_deleted()

    self.setup_click_updates_field(
        '.unarchive', 'deleted', 'null', 'remove_row')

  def setup_deleted(self):
    for project in Project.allowed_by_user(self.user).filter(
        deleted__isnull=False).order_by('name'):
      self.create_row_for_existing(project, 'Un-archive')
