from datetime import timedelta

from djaveDT import now
from djaveReport.date_range_report import DateRangeReport
from tracktime.models.project import Project
from tracktime.models.to_do import get_status_filter
from tracktime.fields import project_field
from tracktime.widgets.project_to_dos_table import ProjectToDosTable


class AllProjectToDos(DateRangeReport):
  def __init__(self, request, nnow=None):
    nnow = nnow or now()

    default_to_date = nnow.date()
    default_from_date = default_to_date - timedelta(days=30)

    to_dos_table = ProjectToDosTable(user=request.user, form_data=request.POST)

    project_filter = project_field(
        request.user, label='Project', required=False)
    status_filter = get_status_filter()

    super().__init__(
        default_from_date, default_to_date, request_get=request.GET,
        filters=[project_filter, status_filter], contents=to_dos_table,
        from_filter_label='Created from')

    project_id = request.GET.get(project_filter.key(), None)
    if project_id:
      to_dos_table.project = Project.live.allowed_by_user(
          request.user).get(pk=project_id)

    status = request.GET.get(status_filter.key(), None)
    if status:
      to_dos_table.status = status

    to_dos_table.created_from_date = self.from_date()
    to_dos_table.created_to_date = self.to_date()

    to_dos_table.populate_rows()
