# This file is for settings that are particular to this site  with the
# exception of passwords, which should be configured in either
# local_settings.py locally or in environment variables on Heroku for stage and
# live.

import os

from djavEmail.users_email_config import UsersEmailConfig


GO_TO_VIEW_AFTER_SIGN_UP = 'projects'

# Staff can just get their email from the same domain regardless of website.
STAFF_EMAIL_FROM_DISPLAY = 'Staff'
STAFF_EMAIL_FROM_USERNAME = 'staff'
STAFF_EMAIL_FROM_DOMAIN = 'tracktimestaff.tech'

# But users should get emails from domains that reflect the domains they
# requested emails from.
TRACK_TIME_USERS = UsersEmailConfig(
    'TrackTime.TECH', 'TrackTime.TECH', 'tracktimeusers.tech',
    'TrackTime.TECH')
USERS_EMAIL_LOOKUP = {
    'http://127.0.0.1:8000': TRACK_TIME_USERS,
    'https://tracktime.tech': TRACK_TIME_USERS}


QUICKBOOKS_CLIENT_ID = os.environ.get('QUICKBOOKS_CLIENT_ID', None)
QUICKBOOKS_CLIENT_SECRET = os.environ.get('QUICKBOOKS_CLIENT_SECRET', None)
# This is just a prototype so the environment will forever be sandbox.
QUICKBOOKS_ENVIRONMENT = 'sandbox'
