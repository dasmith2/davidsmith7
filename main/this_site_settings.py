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
    'Users', 'users', 'tracktimeusers.tech', 'TrackTime.TECH')
USERS_EMAIL_LOOKUP = {
    'http://127.0.0.1:8000': TRACK_TIME_USERS,
    'https://tracktime.tech': TRACK_TIME_USERS}

# Amazon S3 test buckets. Replace these!
from djaveS3.bucket_config import BucketConfig
MAX_WIDTH_OR_HEIGHT = 800
IAM_ACCESS_KEY_ID = os.environ.get('IAM_ACCESS_KEY_ID', '????????????????????')
IAM_SECRET_ACCESS_KEY = os.environ.get(
    'IAM_SECRET_ACCESS_KEY', '????????????????????????????????????????')
PUBLIC_BUCKET_NAME = os.environ.get('PUBLIC_BUCKET_NAME', '???????????????')
PUBLIC_BUCKET = BucketConfig(
    PUBLIC_BUCKET_NAME, IAM_ACCESS_KEY_ID,
    IAM_SECRET_ACCESS_KEY, is_public=True,
    max_width_or_height=MAX_WIDTH_OR_HEIGHT)
PRIVATE_BUCKET_NAME = os.environ.get('PRIVATE_BUCKET_NAME', '????????????????')
PRIVATE_BUCKET = BucketConfig(
    PRIVATE_BUCKET_NAME, IAM_ACCESS_KEY_ID,
    IAM_SECRET_ACCESS_KEY, is_public=False,
    max_width_or_height=MAX_WIDTH_OR_HEIGHT)
S3_BUCKETS = [PRIVATE_BUCKET, PUBLIC_BUCKET]
