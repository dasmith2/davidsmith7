import re


def ignore(name):
  return re.compile(r'__pycache__|\.venv|\.git').findall(name)
