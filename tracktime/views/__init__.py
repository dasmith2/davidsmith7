# flake8: noqa
from tracktime.views.api_docs import api_docs
from tracktime.views.enter_time import enter_time, delete_work_session
from tracktime.views.projects import (
    projects, archived_projects, archive_project, unarchive_project,
    rename_project)
from tracktime.views.report import report, project_work_report
from tracktime.views.settings import settings
from tracktime.views.to_do import (
    to_do, to_do_done, delete_to_do, edit_description,
    to_do_for_another_project)
