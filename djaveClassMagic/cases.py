def upper_case_singular(model):
  return model.__name__


def lower_case_singular(model):
  return upper_case_singular(model).lower()


def upper_case_plural(model):
  return upper_case_singular(model) + 's'


def lower_case_plural(model):
  return upper_case_plural(model).lower()
