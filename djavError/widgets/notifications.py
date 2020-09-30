from djaveCRUDTable.columns import DisplayFieldColumn

from djavError.models.notification import Notification
from djavError.widgets.fixables import Fixables


class Notifications(Fixables):
  def get_model(self):
    return Notification

  def get_leading_columns(self):
    return [DisplayFieldColumn('Title')]
