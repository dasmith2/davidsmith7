from djaveAPI.discover_schema import api_fields, TEXT, CHAR
from djaveTable.table import Table


def field_table(model):
  table = Table([
      'Field', 'Type', 'Description', 'Can filter', 'Required',
      'Not editable'])
  for field in api_fields(model):
    field_type = field.type
    if field_type == CHAR:
      field_type = '{}, max length {}'.format(TEXT, field.max_length)
    can_filter = '' if not field.can_filter else 'Filter'
    editable = '' if field.editable else 'Not editable'
    required = 'Required' if field.required else ''
    table.create_row([
        field.name, field_type, field.help_text, can_filter,
        required, editable])
  return table
