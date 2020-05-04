from django.conf import settings

from djaveS3.bucket_config import BucketConfig


class GetBucketConfigException(Exception):
  pass


def get_bucket_config(bucket):
  if isinstance(bucket, BucketConfig):
    return bucket
  if not hasattr(settings, 'S3_BUCKETS'):
    message = ''.join([
        'You need to configure your S3_BUCKETS in django.conf.settings. For '
        'example,\nfrom djaveS3.bucket_config import BucketConfig\n'
        'S3_BUCKETS = [BucketConfig(\'my_bucket_name\', '
        'my_access_key_id, my_secret_access_key, is_public=True)]'])
    raise GetBucketConfigException(message)
  if isinstance(bucket, str):
    got_bucket = None
    for next_bucket in settings.S3_BUCKETS:
      if next_bucket.bucket_name == bucket:
        got_bucket = next_bucket
    if got_bucket is None:
      raise GetBucketConfigException((
          'S3 bucket {} is not configured in S3_BUCKETS in '
          'django.conf.settings').format(bucket))
    if not isinstance(got_bucket, BucketConfig):
      raise GetBucketConfigException((
          'S3 bucket {} in S3_BUCKETS in django.conf.settings should be a '
          'BucketConfig, but it is a {}').format(got_bucket.__class__))
    return got_bucket
  raise GetBucketConfigException(
      'I am expecting a BucketConfig or a string. You gave me a {}'.format(
          bucket.__class__))
