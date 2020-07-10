from djaveDT import now


def set_fixable_stuff(fixable, **kwargs):
  fixable.count = kwargs.get('count', 1)
  fixable.latest = kwargs.get('latest', now())
  fixable.fixed = kwargs.get('fixed', None)
  fixable.save()
  return fixable
