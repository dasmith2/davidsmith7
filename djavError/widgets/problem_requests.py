from djavError.widgets.fixable_report import FixableTable


class ProblemRequestsTable(FixableTable):
  def headers(self):
    return ['Path', 'Method', 'Latest', 'Count', 'Variables']

  def get_cells(self, fixable):
    return [
        fixable.path, fixable.method, fixable.latest, fixable.count,
        fixable.variables]
