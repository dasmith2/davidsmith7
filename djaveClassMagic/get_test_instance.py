from django.conf import settings
from djaveClassMagic.model_fields import (
    model_fields, DATE_TIME, DATE, FLOAT, INTEGER, TEXT, CHAR, BOOLEAN)
from djaveDT import now


def get_test_instance(cls, **kwargs):
  """ kwargs is where you set specific fields. For instance,
  get_test_instance(Project, name='Bobs science laboratory')

  kwargs gets applied to nested, unspecified objects too. So if you do, like,
  get_test_instance(
      ProjectToDo, name='Bobs science laboratory',
      description='Streamline accessioning')
  then it'll create a ProjectToDo whose description is 'Streamline...', then
  since ProjectToDo has a required foreign key to Project, it'll create
  a Project whose name is 'Bobs science laboratory'. Of course in this case
  you could also approach it like this:
  bobs = get_test_instance(Project, name='Bobs science laboratory')
  get_test_instance(ProjectToDo, project=bobs, description='Streamline') """

  if settings.PROD:
    raise Exception('Do not create test instances in production.')
  if not settings.TEST:
    # This MAY be helpful to notice when you're accidentally creating a bunch
    # of test whatevers in a persistent database.
    print('About to get_test_instance({}, **{})'.format(cls, kwargs))

  instance = cls()
  for field in model_fields(cls):
    if field.name == 'created':
      # Created is typically set automatically, so in order to set it manually
      # I have to use an update call on an existing object.
      pass
    elif field.name in kwargs:
      setattr(instance, field.name, kwargs[field.name])
    elif field.name in ('id', 'deleted'):
      # It's a new instance, so by default, don't set the id and don't delete
      # it. But keep this below the field.name in kwargs check so you can set
      # deleted if you want.
      pass
    elif not field.required:
      pass
    elif field.foreign_key_to:
      setattr(instance, field.name, get_test_instance(
          field.foreign_key_to, **kwargs))
    else:
      if field.type == DATE_TIME:
        value = now()
      elif field.type == DATE:
        value = now().date()
      elif field.type == FLOAT:
        value = 3.21
      elif field.type == INTEGER:
        value = 4
      elif field.type == TEXT:
        value = 'Hellooo world!'
      elif field.type == CHAR:
        value = 'Hello world!'
      elif field.type == BOOLEAN:
        value = True
        if field.default is False:
          value = field.default
      else:
        raise Exception(
            'I dont know how to handle a {} field yet'.format(field.type))
      if value is None:
        raise Exception(
            'This logic didnt tell me what value to set {}.{} to'.format(
                cls, field.name))
      setattr(instance, field.name, value)
  instance.save()

  if 'created' in kwargs:
    cls.objects.filter(pk=instance.pk).update(created=kwargs['created'])

  return instance
