"""
I want to sync the QuickBooks example business to my local database.

Luckily, there are a bunch of similarities between the different
Quickbooks objects that I can take advantage of to cut down on the
boilerplate. So this is an abstract class you should inherit from
if you want to pull, for example, QuickBooks Customers.

In fact, this base class stuff is tested by the specific example of
quickbooks2/models/test_customer.py
"""

from djaveAPI.models.publishable import Publishable
from djaveClassMagic.model_fields import model_fields
from django.contrib.auth.models import User
from django.db import models
from django.shortcuts import reverse
from djaveDT import now

from quickbooks2.get_quickbooks_client import get_quickbooks_client


class QuickBooksObject(Publishable):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  qb_id = models.PositiveIntegerField(db_index=True)
  last_synced = models.DateTimeField()

  @classmethod
  def get_quickbooks_class(cls):
    raise NotImplementedError(
        'QuickBooksObject relies on class magic to cut down on the '
        'boilerplate, so you need to say which quickbooks.objects.* class '
        'your child class is talking about.')

  def populate_extra_fields(self, obj_from_quickbooks):
    """ You can override this function to do more complex parsing of attributes
    than simply copying properties with the exact same name. """
    pass

  def populate_fields_with_exact_same_name(self, obj_from_quickbooks):
    for model_field in model_fields(self.__class__):
      if hasattr(obj_from_quickbooks, model_field.name):
        setattr(self, model_field.name, getattr(
            obj_from_quickbooks, model_field.name))

  def populate_fields(self, obj_from_quickbooks):
    self.populate_fields_with_exact_same_name(obj_from_quickbooks)
    self.populate_extra_fields(obj_from_quickbooks)

  @classmethod
  def filter_allowed_by_user(cls, user, query_set):
    return query_set.filter(user=user)

  def allowed_api_keys(self, api_key_type):
    return []

  @classmethod
  def retrieve_all(cls, user, protocol_and_host):
    """ Get and return the list of cls.get_quickbooks_class() (e.g.
    quickbooks.objects.Customer) from QuickBooks. """
    qb_client = get_quickbooks_client(user, protocol_and_host)
    return cls.get_quickbooks_class().filter(Active=True, qb=qb_client)

  @classmethod
  def merge_list(cls, user, quickbooks_objects, nnow=None):
    """ Actually put the given cls.get_quickbooks_class()s
    (e.g. quickbooks.objects.Customer) in our database.
    quickbooks_objects should be the results of retrieve_all. """

    nnow = nnow or now()

    for qb_obj in quickbooks_objects:
      qb_id = qb_obj.Id
      local_obj = cls.allowed_by_user(user).filter(qb_id=qb_id).first()
      if not local_obj:
        local_obj = cls(user=user, qb_id=qb_id)

      if qb_obj.Active:
        local_obj.deleted = None
      elif not local_obj.deleted:
        local_obj.deleted = nnow

      local_obj.last_synced = nnow

      local_obj.populate_fields(qb_obj)

      local_obj.save()

  @classmethod
  def merge_all(cls, user, protocol_and_host):
    cls.merge_list(user, cls.retrieve_all(user, protocol_and_host))

  def add_to_json(self, data):
    data['url'] = self.url()

  def url(self):
    return reverse('quickbooks2_model_instance', kwargs={
        'model_name': self._meta.model_name, 'pk': self.pk})

  class Meta:
    abstract = True
    unique_together = [('user', 'qb_id')]
