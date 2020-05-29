from datetime import date

from django.db import models
from django_fake_model import models as fake_models
from djaveDT import to_tz_dt
from djaveTest import TestCase

from djaveAPI.models.publishable import Publishable
from djaveAPI.models.user_api_key import UserAPIKey
from djaveAPI.save import update, save_new


class MyOtherFakeModel(fake_models.FakeModel):
  name = models.CharField(max_length=100)

  @classmethod
  def allowed(cls, api_key):
    return cls.objects.all()


class MyFakeModel(fake_models.FakeModel, Publishable):
  small_int = models.IntegerField()
  large_int = models.IntegerField(null=True, blank=True)
  my_date = models.DateField()
  my_date_time = models.DateTimeField()
  my_char = models.CharField(max_length=100)
  my_text = models.TextField()
  my_other_fake_model = models.ForeignKey(
      MyOtherFakeModel, on_delete=models.CASCADE)

  def explain_why_invalid(self):
    if self.large_int and self.small_int > self.large_int:
      return 'small_int should be less than large_int'

  @classmethod
  def allowed(cls, api_key):
    return cls.objects.all()


def get_test_my_other_fake_model(**kwargs):
  return MyOtherFakeModel.objects.create(**kwargs)


def get_test_my_fake_model(save=True, **kwargs):
  my_other_fake_model = kwargs.get('my_other_fake_model', None)
  if not my_other_fake_model:
    my_other_fake_model = get_test_my_other_fake_model(**kwargs)
  instance = MyFakeModel(
      small_int=kwargs.get('small_int', 10),
      large_int=kwargs.get('large_int', 20),
      my_date=kwargs.get('my_date', date(2020, 1, 1)),
      my_date_time=kwargs.get('my_date_time', to_tz_dt('2020-01-01 12:00')),
      my_char=kwargs.get('my_char', 'hello'),
      my_text=kwargs.get('my_text', 'world'),
      my_other_fake_model=my_other_fake_model)
  if save:
    instance.save()
  return instance


@MyFakeModel.fake_me
@MyOtherFakeModel.fake_me
class SaveTests(TestCase):
  def setUp(self):
    super().setUp()
    self.other_other = get_test_my_other_fake_model(name='Other other')
    self.request_POST = {
        'small_int': 1,
        'large_int': 2,
        'my_date': '2020-05-28',
        'my_date_time': '2020-05-28T12:00:00.000000-04:00',
        'my_char': 'Gourmet surprise',
        'my_text': 'for dinner',
        'my_other_fake_model': self.other_other.pk}

  def test_update(self):
    instance = get_test_my_fake_model(save=True)
    self.assertEqual(instance, update(
        instance, self.request_POST, UserAPIKey()))
    self._test_matches_self_request_POST(instance)

    instance.refresh_from_db()
    self.assertEqual(1, instance.small_int)

  def test_save_new(self):
    instance = save_new(MyFakeModel, self.request_POST, UserAPIKey())
    self._test_matches_self_request_POST(instance)
    self.assertTrue(instance.pk > 0)

  def _test_matches_self_request_POST(self, instance):
    self.assertEqual(1, instance.small_int)
    self.assertEqual(2, instance.large_int)
    self.assertEqual(date(2020, 5, 28), instance.my_date)
    self.assertEqual(
        to_tz_dt('2020-05-28T12:00:00.000000-04:00'), instance.my_date_time)
    self.assertEqual('Gourmet surprise', instance.my_char)
    self.assertEqual('for dinner', instance.my_text)
    self.assertEqual(self.other_other, instance.my_other_fake_model)
