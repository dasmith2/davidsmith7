""" Things get a little messy wiring Django's User class up to the API. Your
best bet is to do something like this.

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from djaveAllowed.models import Allowed
from djaveClassMagic.one_to_one_or_none_field import OneToOneOrNoneField


@receiver(post_save, sender=User)
def save_my_user(sender, instance, **kwargs):
  if not instance.myuser_or_none:
    MyUser.objects.create(user=instance)


class MyUser(Publishable):
  user = OneToOneOrNoneField(User, primary_key=True, on_delete=models.CASCADE)
  # You can add whatever custom user fields you need for your app here.

  def add_to_json(self, as_dict):
    as_dict['username'] = self.user.username

  @classmethod
  def filter_allowed_by_user(cls, user, query_set):
    return query_set.filter(user=user)  # Or whatever


Then, because MyUser.user is a primary_key, this API library is smart enough
to publish MyUser like this, using the exact same id for the Django user and
the MyUser.

{'type': 'MyUser', 'id': self.user.id, <your custom user fields>}

Now, it's best to get your equivalent of MyUser in right away so your other
models can have a foreign key to MyUser (or whatever) instead of the Django
User model.

class Project(Publishable):
  user = OneToOneOrNoneField(MyUser)

Then the API can take advantage of MyUser.filter_allowed_by_user to enforce
permissions when somebody uses the API to assign a Project to a User, say. If
you're reading this too late, you MAY be able to get get away with your objects
referencing Django's User model AS LONG AS no object is ever reassigned from
one user to another, your users only ever use the magic string 'me' in the API
to refer to themselves for new objects, and otherwise never specify a user,
thus allowing the API to leave the existing user variables untouched. """
