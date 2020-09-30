from djaveHTML.field import SelectField, Option

from invoice.models.invoice import STATUSES, STATUS_TOOLTIP


def status_field(query_key=None):
  return SelectField(
      key_prefix='status', options=status_options(), required=False,
      label=STATUS_TOOLTIP, query_key=query_key or 'status')


def status_options():
  return [Option(option, option) for option in STATUSES]
