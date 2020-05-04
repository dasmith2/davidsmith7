""" Put random checks in here that should pass before the app deploys. """

import re
import sys


requirements_file = open('requirements.txt').read()

ABNORMAL = 1

if re.compile(r'\nDjango\s*=').search(requirements_file):
  print(
      'In requirements.txt, change Django=... to django=... The stage '
      'environment of Heroku chokes on the upper case Django during automatic '
      'deployment for some reason.')
  sys.exit(ABNORMAL)

if re.compile(r'\nselenium\s*=').search(requirements_file):
  print(
      'You can\'t have selenium in the requirements file. The stage '
      'environment of Heroku chokes on it during automatic deployment. In '
      'order to have selenium locally, python -m pip install selenium, but '
      'leave selenium out of requirements.txt')
  sys.exit(ABNORMAL)
