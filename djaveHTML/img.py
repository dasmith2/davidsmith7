from djaveHTML.element import Element


class Img(Element):
  def __init__(self, img_src):
    self.img_src = img_src

  def as_html(self):
    return '<img src="{}" height="100">'.format(self.img_src)

  def as_csv(self):
    return self.img_src
