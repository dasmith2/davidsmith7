from djaveCRUDTable.columns import DisplayFieldColumn

from tracktime.fields import project_field, hours_field


class ProjectColumn(DisplayFieldColumn):
  def __init__(self, user):
    self.user = user
    super().__init__('Project', 'project_name')

  def inline_create_cell(self):
    project_filter = project_field(self.user, has_to_do_list=True)
    return self.td_around('project', project_filter.as_html())


class HoursColumn(DisplayFieldColumn):
  def __init__(self):
    super().__init__(
        'Hours', 'time_entry_description',
        header_css_class='hours_header', cell_css_class='width-135 hours')

  def inline_create_cell(self):
    return self.td_around('hours', hours_field().as_html())
