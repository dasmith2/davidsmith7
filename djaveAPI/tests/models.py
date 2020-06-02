"""
I needed some test models that would get installed in tests but not in
production. If you look in main/settings.py you'll see

if TEST:
  INSTALLED_APPS.append('djaveAPI.tests.apps.DjaveAPITestsConfig')

djaveAPI.tests.apps was a finicky thing to get right.
"""
from datetime import date

from django.contrib.auth.models import User
from django.db import models
from djaveAPI.models.publishable import Publishable
from djaveAPI.models.user_api_key import UserAPIKey
from djaveDT import to_tz_dt
from djaveTest import get_test_user


class MyFakeModel(Publishable):
  name = models.CharField(max_length=100)
  user = models.ForeignKey(User, on_delete=models.CASCADE)

  @classmethod
  def allowed(cls, api_key):
    if isinstance(api_key, UserAPIKey):
      return cls.all.filter(user=api_key.user)
    raise Exception(api_key.__class__)

  @classmethod
  def new_instance(cls):
    return cls()

  def allowed_api_keys(self, api_key_type):
    if api_key_type is UserAPIKey:
      return api_key_type.objects.filter(user=self.user)
    raise Exception(api_key_type)


def get_test_my_fake_model(**kwargs):
  user = kwargs.get('user', None)
  if not user:
    user = get_test_user()
  return MyFakeModel.all.create(name=kwargs.get('name', 'Testname'), user=user)


class ComplexFakeModel(Publishable):
  small_int = models.IntegerField()
  large_int = models.IntegerField(null=True, blank=True)
  my_date = models.DateField()
  my_date_time = models.DateTimeField()
  my_char = models.CharField(max_length=100)
  my_text = models.TextField()
  my_fake_model = models.ForeignKey(MyFakeModel, on_delete=models.CASCADE)

  def explain_why_invalid(self):
    if self.large_int and self.small_int > self.large_int:
      return 'small_int should be less than large_int'

  @classmethod
  def allowed(cls, api_key):
    return cls.objects.all()

  def allowed_api_keys(self, api_key_type):
    return api_key_type.objects.all()


def get_test_complex_fake_model(save=True, **kwargs):
  my_fake_model = kwargs.get('my_fake_model', None)
  if not my_fake_model:
    my_fake_model = get_test_my_fake_model(**kwargs)
  instance = ComplexFakeModel(
      small_int=kwargs.get('small_int', 10),
      large_int=kwargs.get('large_int', 20),
      my_date=kwargs.get('my_date', date(2020, 1, 1)),
      my_date_time=kwargs.get('my_date_time', to_tz_dt('2020-01-01 12:00')),
      my_char=kwargs.get('my_char', 'hello'),
      my_text=kwargs.get('my_text', 'world'),
      my_fake_model=my_fake_model)
  if save:
    instance.save()
  return instance
