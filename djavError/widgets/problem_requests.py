from djaveCRUDTable.columns import DisplayFieldColumn
from djavError.widgets.fixables import Fixables


class ProblemRequests(Fixables):
  def get_leading_columns(self):
    return [
        DisplayFieldColumn('Path'),
        DisplayFieldColumn('Method')]

  def get_tail_columns(self):
    return [DisplayFieldColumn('Variables')]
