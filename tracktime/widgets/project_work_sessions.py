from django.shortcuts import reverse
from djaveCRUDTable.columns import DisplayFieldColumn
from djaveCRUDTable.crud_table import CRUDTable

from tracktime.fields import project_field
from tracktime.models.project_to_do import ProjectToDo
from tracktime.widgets.project_work_summary import visible_filters


class ProjectWorkSessions(CRUDTable):
  def __init__(self, user):
    display_columns = [DisplayFieldColumn('Description')]
    project_filter = project_field(user, required=False, use_clock=True)
    vis_filters = visible_filters() + [project_filter]
    super().__init__(
        ProjectToDo, display_columns, visible_filters=vis_filters,
        can_create_new=False, list_url=reverse('project_work_report'),
        list_api_url=reverse('project_work_session_description_data'),
        nav_css_class='project_work_summary_nav', show_column_headers=False,
        modified_row_callback='modified_project_work_report_row_callback',
        fetch_list_callback='fetch_project_work_report_list_callback')
