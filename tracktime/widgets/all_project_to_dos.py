from datetime import timedelta

from djaveDT import now
from djaveReport.date_range_report import DateRangeReport
from tracktime.models.project import Project
from tracktime.models.to_do import get_status_filter, NOT_DONE
from tracktime.fields import project_field
from tracktime.widgets.project_to_dos_table import ProjectToDosTable


class AllProjectToDos(DateRangeReport):
  def __init__(self, user, request_GET, request_POST, nnow=None):
    nnow = nnow or now()

    default_to_date = nnow.date()
    default_from_date = default_to_date - timedelta(days=180)

    to_dos_table = ProjectToDosTable(user=user, form_data=request_POST)

    project_filter = project_field(
        user, label='Project', required=False, has_to_do_list=True)
    status_filter = get_status_filter(default=NOT_DONE)

    super().__init__(
        default_from_date, default_to_date, request_get=request_GET,
        filters=[project_filter, status_filter], contents=to_dos_table)

    project_id = request_GET.get(project_filter.key(), None)
    if project_id:
      to_dos_table.project = Project.live.allowed_by_user(
          user).get(pk=project_id)

    status = request_GET.get(status_filter.key(), status_filter.default)
    if status:
      to_dos_table.status = status

    to_dos_table.created_from_date = self.from_date()
    to_dos_table.created_to_date = self.to_date()

    to_dos_table.populate_rows()
