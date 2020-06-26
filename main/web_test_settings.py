# flake8: noqa
""" The entire point of this file is so I can do
./manage.py runserver --settings main.web_test_settings
And the entire point of THAT is so that main/settings.py can do
WEB_TEST = 'main.web_test_settings' in sys.argv
And the entire point of THAT is so I can not include the django toolbar in web
tests. And the entire point of THAT is to make my demos look good. """

from main.settings import *
