from djaveTable.cell_content import CellContent


class Problem(CellContent):
  def __init__(self, text):
    self.text = text

  def as_html(self):
    return '<span class="problem">{}</span>'.format(self.text)

  def as_csv(self):
    return ''
