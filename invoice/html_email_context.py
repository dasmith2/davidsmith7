""" This attempts to take some of the pain out of writing HTML emails where all
styles must be inlined. """
from django.utils.safestring import mark_safe


def html_context():
  open_div_style = 'font-family: Arial; margin-top: 60px;'
  open_table_style = 'border-collapse: collapse; border: 1px solid #999;'
  open_cell_style = 'border: 1px solid #999; padding: 7px;'
  stuff = {
      'open_div_style': open_div_style,
      'open_div': '<div style="{}">'.format(open_div_style),
      'open_table_style': open_table_style,
      'open_table': '<table style="{}">'.format(open_table_style),
      'open_cell_style': open_cell_style,
      'open_cell': '<td style="{}">'.format(open_cell_style)}
  for key in stuff:
    stuff[key] = mark_safe(stuff[key])
  return stuff
