from djaveAPI.models.api_key import APIKey
from djaveTest import TestCase


class APIKeyTests(TestCase):
  def test_generate_and_use_key(self):
    key = APIKey.objects.create_key('Trailer park supervision')
    username = key.username
    plain_password = key.get_plain_password()

    self.assertEqual(key, APIKey.objects.get_api_key(username, plain_password))
    self.assertIsNone(APIKey.objects.get_api_key('wrong', plain_password))
    self.assertIsNone(APIKey.objects.get_api_key(username, 'wrong'))

    key.refresh_from_db()
    try:
      key.get_plain_password()
    except Exception:
      # You can only get the plain password immediately after you creating the
      # key because we only store hashed passwords in the database.
      pass
    self.assertEqual('Trailer park supervision', key.name)
