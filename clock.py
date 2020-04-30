"""
This is basically our cron. It's in New York time.

Error reporting isn't perfect here. Lint catches syntax errors, the deploy
process catches import errors, and as long as the functions you import and run
are decorated with @background or @background_command then any exceptions they
raise will get emailed. But there are still cracks in the system you can sneak
bugs into, such as running a @background function that's on a models.Manager.
See util/background.py for a more detailed explanation of why that fails
specifically, but the point is, it is possible to swallow errors here, so be
careful. Follow conventions. Don't get fancy.

If something fishy is going on despite all the precautions, check the logs.

heroku logs -d clock -t -a <this-heroku-app-name e.g. davidsmith7-stage>

You can also look in the commands/models#CommandRun table to ensure your
@background_command is running successfully.

You can't import background here because any function you decorate with it will
trigger "Functions from the __main__ module cannot be processed by workers".
So you have to import functions that are decorated with background. And they
all should be, because the clock itself should never do any actual work. It
should only kick tasks off to background threads.

Hence, no work may be placed directly in this file. This file is strictly for
scheduling.

Cron scheduling:
https://apscheduler.readthedocs.io/en/latest/modules/triggers/cron.html

Interval scheduling:
https://apscheduler.readthedocs.io/en/latest/modules/triggers/interval.html

Uh, it seems to me that interval scheduling is not very reliable. I'm looking
at a case where it went 3 hours and 8 minutes for the 1 hour interval scheduled
fix_stale, and there wasn't anything happening to block it or anything. But
that could also be our reddis provider.

This file is the entire reason we have flake8 (./lint.sh) globally ignore
E402 module level import not at top of file
"""
import os
import sys

import django

# Otherwise you get "django.core.exceptions.ImproperlyConfigured: Requested
# setting INSTALLED_APPS, but settings are not configured. You must either
# define the environment variable DJANGO_SETTINGS_MODULE or call
# settings.configure() before accessing settings."
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()


from apscheduler.schedulers.blocking import BlockingScheduler
from djaves3.models import (
    clean_up_never_used, clean_up_no_longer_needed, resize_all)


sched = BlockingScheduler()


@sched.scheduled_job('cron', hour='1')
def photo_stuff():
  clean_up_never_used()
  clean_up_no_longer_needed()
  resize_all()


# test.sh fires this file up with --no-run so continuous integration breaks
# when this file contains import errors.
if '--no-run' not in sys.argv:
  sched.start()
