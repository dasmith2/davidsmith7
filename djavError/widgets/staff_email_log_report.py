from djavError.widgets.fixable_report import FixableTable


class StaffEmailLogTable(FixableTable):
  def headers(self):
    return ['Title', 'Created', 'Latest', 'Count']

  def get_cells(self, fixable):
    return [fixable.title, fixable.created, fixable.latest, fixable.count]
