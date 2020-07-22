from django.shortcuts import reverse
from djaveForm.button import Button
from djaveTable.cell_content import InHref
from djaveTable.simple_list import SimpleList

from tracktime.models.project import Project
from tracktime.models.project_work_session import start_clock_on_project


class ToDoProjectPicker(SimpleList):
  def __init__(self, user, request_POST):
    buttons = []
    self.has_projects = False
    for project in Project.live.allowed_by_user(user).filter(
        has_to_do_list=True).order_by('name'):
      self.has_projects = True
      button = None
      if project.use_clock:
        button = Button(
            'Punch in: {}'.format(project.name), button_type='submit')
        if button.get_was_clicked(request_POST):
          start_clock_on_project(user, project)
      else:
        url = reverse('to_do', kwargs={'project_pk': project.pk})
        button = InHref(project.name, url, button=True)
      buttons.append(button)
    super().__init__(buttons)
