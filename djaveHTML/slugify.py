import re


def slugify(text):
  return re.compile(r'[^\w]').sub('', text).lower()
