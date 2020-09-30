from djaveHTML.element import TagElement


class H1(TagElement):
  def tag_name(self):
    return 'h1'


class H2(TagElement):
  def tag_name(self):
    return 'h2'
