from unittest.mock import Mock

from django_fake_model import models as fake_models
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from djaveAPI.models.publishable import Publishable
from djaveAPI.models.pretend_publishable import PretendPublishable
from djaveAPI.models.webhook import Webhook
from djaveAPI.post import post
from djaveAPI.tests.test_user_api_key import get_test_user_api_key
from djaveDT import to_tz_dt
from djaveTest import get_test_user, TestCase


class MyFakeModel(fake_models.FakeModel, Publishable):
  name = models.CharField(max_length=100)

  @classmethod
  def allowed(cls, api_key):
    return cls.all.all()

  def allowed_api_keys(self, api_key_type):
    return api_key_type.objects.all()


def get_test_my_fake_model(**kwargs):
  return MyFakeModel.all.create(name=kwargs.get('name', 'Testname'))


@MyFakeModel.fake_me
class CreateTests(TestCase):
  def test_create_webhooks(self):
    user = get_test_user()
    get_test_user_api_key(user=user, webhook_url='https://test')
    self.assertEqual(0, Webhook.objects.count())
    obj = get_test_my_fake_model()
    for i in range(2):
      obj.save()

    obj_type = ContentType.objects.get_for_model(MyFakeModel)

    self.assertEqual(1, Webhook.objects.count())
    webhook = Webhook.objects.get(
        obj_id=obj.pk,
        obj_type=obj_type,
        webhook_url='https://test',
        last_send_attempt_at=None,
        attempts=0,
        success_at=None)
    self.assertTrue(webhook.payload.find('Testname') > 0)

    obj.name = 'Tarstneme'
    for i in range(3):
      obj.save()
    self.assertEqual(2, Webhook.objects.count())
    next_webhook = Webhook.objects.get(
        ~Q(pk=webhook.pk),
        obj_id=obj.pk,
        obj_type=obj_type,
        webhook_url='https://test',
        last_send_attempt_at=None,
        attempts=0,
        success_at=None)
    self.assertTrue(next_webhook.payload.find('Tarstneme') > 0)


@MyFakeModel.fake_me
class SendTests(TestCase):
  def test_send(self):
    user = get_test_user()
    get_test_user_api_key(user=user, webhook_url='https://test')
    get_test_my_fake_model()

    _post = Mock(spec=post)
    _post.returnValue = True
    Webhook.objects.send(_post=_post, nnow=to_tz_dt('2020-01-15 12:00'))

    self.assertEqual(1, Webhook.objects.count())
    self.assertEqual(1, Webhook.objects.filter(
        last_send_attempt_at=to_tz_dt('2020-01-15 12:00'),
        attempts=1,
        success_at=to_tz_dt('2020-01-15 12:00')).count())


class PretendPublishableTests(TestCase):
  pass
