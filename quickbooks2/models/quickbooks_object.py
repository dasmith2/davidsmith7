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


class BaseQuickBooksObject(Publishable):
  qb_id = models.PositiveIntegerField(db_index=True)
  last_synced = models.DateTimeField()

  # In your subclass, you can put fields with the exact same name as the
  # QuickBooks definition and it'll auto-populate when you pull. But this does
  # require you to capitalize things weird. For instance, the Account model has
  # Classification = models.CharField(max_length=200, default='')

  @classmethod
  def get_quickbooks_class(cls):
    raise NotImplementedError(
        'QuickBooksObject relies on class magic to cut down on the '
        'boilerplate, so you need to say which quickbooks.objects.* class '
        'your child class is talking about.')

  @classmethod
  def top_level_object(cls):
    """" Should this object get its own navigation header? For example, there
    should be a Bills navigation item, but there shouldn't be a
    quickbooks2.models.bill.Line header because Lines only make sense in the
    context of a specific Bill. """
    return True

  def copy_non_obvious_data(self, obj_from_quickbooks, nnow=None):
    """ You can override this function to do more complex parsing of attributes
    than simply copying properties with the exact same name. """
    pass

  def copy_fields_with_exact_same_name(self, obj_from_quickbooks):
    for model_field in model_fields(self.__class__):
      if hasattr(obj_from_quickbooks, model_field.name):
        value = getattr(obj_from_quickbooks, model_field.name)
        if model_field.foreign_key_to:
          qb_id = value.to_dict()['value']  # e.g., '46'
          value = model_field.foreign_key_to.objects.get(qb_id=qb_id)
        setattr(self, model_field.name, value)

  def copy_data(self, obj_from_quickbooks, user, nnow=None):
    self.copy_fields_with_exact_same_name(obj_from_quickbooks)
    self.copy_non_obvious_data(obj_from_quickbooks, nnow=nnow)

  def allowed_api_keys(self, api_key_type):
    return []

  @classmethod
  def retrieve_all(cls, user, protocol_and_host):
    """ Get and return the list of cls.get_quickbooks_class() (e.g.
    quickbooks.objects.Customer) from QuickBooks. So for example,
    from quickbooks.objects.customer import Customer as QBCustomer
    class Customer(QuickBooksObject):
      @classmethod
      def get_quickbooks_class(cls):
        return QBCustomer

    Customer.retrieve_all(user, 'https://whatever')
    """

    def do_retrieve(use_qb_client):
      """ e.g. QBCustomer.filter(qb=use_qb_client) """
      return cls.get_quickbooks_class().filter(qb=use_qb_client)

    return cls.get_user_credentials(user).do_query(
        protocol_and_host, do_retrieve)

  @classmethod
  def retrieve_one(cls, user, protocol_and_host, Id):

    def do_retrieve_one(qb):
      return cls.get_quickbooks_class().get(Id)

    return cls.get_user_credentials(user).do_query(
        protocol_and_host, do_retrieve_one)

  @classmethod
  def get_user_credentials(cls, user):
    user_credentials = user.usercredentials_or_none
    if not user_credentials:
      raise Exception((
          '{} doesnt have any UserCredentials for Quickbooks so they probably '
          'havent authorized quickbooks yet, so I cant possibly query their '
          'QuickBooks.').format(user))
    return user_credentials

  @classmethod
  def merge_list(cls, user, quickbooks_objects, nnow=None):
    """ Actually put the given cls.get_quickbooks_class()s
    (e.g. quickbooks.objects.Customer) in our database.
    quickbooks_objects should be the results of retrieve_all. """

    for qb_obj in quickbooks_objects:
      cls.merge_obj(user, qb_obj, nnow=nnow)

  @classmethod
  def merge_obj(cls, user, qb_obj, nnow=None, **new_kwargs):
    """ new_kwargs are passed directly to the constructor if we have to make a
    new object. This is important for nested list type objects. For instance, I
    need a way for a Line to get created with the appropriate Bill. """
    nnow = nnow or now()

    qb_id = qb_obj.Id
    # For example, the first Line of every Bill has qb_id 1, so you also need
    # to filter by bill=bill to find an existing object. Otherwise all Lines
    # will always go under the same Bill basically.
    local_obj = cls.allowed_by_user(user).filter(
        qb_id=qb_id, **new_kwargs).first()
    if not local_obj:
      local_obj = cls(qb_id=qb_id, **new_kwargs)

    if hasattr(qb_obj, 'Active'):
      if qb_obj.Active:
        local_obj.deleted = None
      elif not local_obj.deleted:
        local_obj.deleted = nnow

    local_obj.last_synced = nnow

    local_obj.copy_data(qb_obj, user, nnow=nnow)

    local_obj.save()

  @classmethod
  def merge_all(cls, user, protocol_and_host):
    cls.merge_list(user, cls.retrieve_all(user, protocol_and_host))

  def select_related_list(self):
    to_return = []
    for model_field in model_fields(self.__class__):
      if model_field.foreign_key_to:
        to_return.append(model_field.name)
    return to_return

  def add_to_json(self, data):
    data['url'] = self.url()
    for field in model_fields(self.__class__):
      if field.foreign_key_to:
        foreign_obj = getattr(self, field.name)
        url_attr = '{}_url'.format(field.name)
        str_attr = '{}_str'.format(field.name)
        if hasattr(foreign_obj, 'url'):
          data[url_attr] = foreign_obj.url()
          data[str_attr] = str(foreign_obj)
        elif foreign_obj is None:
          data[url_attr] = None
          data[str_attr] = None

  def url(self):
    return reverse('quickbooks2_model_instance', kwargs={
        'model_name': self._meta.model_name, 'pk': self.pk})

  class Meta:
    abstract = True


class QuickBooksObject(BaseQuickBooksObject):
  sync_token = models.CharField(max_length=200, default='')
  user = models.ForeignKey(User, on_delete=models.CASCADE)

  def copy_data(self, qb_obj, user, nnow=None):
    self.sync_token = qb_obj.SyncToken
    self.user = user
    super().copy_data(qb_obj, user, nnow=nnow)

  class Meta:
    abstract = True
    unique_together = [('user', 'qb_id')]

  @classmethod
  def filter_allowed_by_user(cls, user, query_set):
    return query_set.filter(user=user)


class NestedListQuickBooksObject(BaseQuickBooksObject):
  @classmethod
  def nested_under_model(cls):
    raise NotImplementedError('nested_under_model')

  class Meta:
    abstract = True
