from django.shortcuts import reverse
from djaveURL import is_valid_url


NEXT_URL = 'next_url'


def get_logout_url(request_get_full_path):
  return append_next_url(reverse('djave_logout'), request_get_full_path)


def append_next_url(url, next_url):
  if not next_url:
    return url
  if not is_valid_url(next_url):
    raise Exception(
        'I double checked, and {} is not a valid next_url'.format(next_url))
  return '{}?{}={}'.format(url, NEXT_URL, next_url)
