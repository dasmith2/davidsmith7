from django.contrib.auth.hashers import make_password
from djaveTest.unit_test import random_string


def set_api_key_stuff(api_key, **kwargs):
  api_key.username = kwargs.get('username', random_string())
  plain_password = kwargs.get('plain_password', None)
  hashed_password = kwargs.get('hashed_password', None)
  if plain_password and not hashed_password:
    hashed_password = make_password(plain_password)
  if not hashed_password:
    hashed_password = make_password('asdf1234')
  if plain_password:
    api_key.set_plain_password(plain_password)
  api_key.hashed_password = hashed_password
  api_key.webhook_url = kwargs.get('webhook_url', '')
  api_key.save()
  return api_key
