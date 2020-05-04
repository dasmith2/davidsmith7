import base64
import os
import re

import boto3
import botocore
from django.conf import settings
from django.db import models
from django.shortcuts import reverse

from djaveS3.get_bucket_config import get_bucket_config


s3_region_name = 'us-east-2'
if hasattr(settings, S3_REGION_NAME):
  s3_region_name = settings.S3_REGION_NAME
else:
  raise Exception(
      'You need to put S3_REGION_NAME in your settings. An example is '
      'us-east-2')

# You need signature_version='s3v4' to avoid "The authorization mechanism you
# have provided is not supported. Please use AWS4-HMAC-SHA256
_s3_config = botocore.client.Config(
    signature_version='s3v4',
    region_name=s3_region_name)


def get_boto_3_client(bucket):
  # bucket can be a bucket name or a bucket config
  bucket_config = get_bucket_config(bucket)
  return boto3.client(
      's3',
      aws_access_key_id=bucket_config.access_key_id,
      aws_secret_access_key=settings.secret_access_key,
      config=_s3_config)


def public_file_url(bucket, file_name):
  # bucket can be a bucket name or a bucket config
  bucket_config = get_bucket_config(bucket)
  if bucket_config.is_sensitive:
    raise Exception(
        'There is no public file url for files in sensitive buckets')
  return 'https://{}.s3.amazonaws.com/{}'.format(
      bucket_config.bucket_name, file_name)


""" Why isn't there a sensitive_file_url(bucket, file_name) function? That's
because sensitive files require security checks, and I don't know what business
rules your organization has, so I can't write a view for you that will display
a sensitive file, so I don't know what view to reverse, so I can't calculate a
sensitive_file_url for you. See sensitive_image_response in djaveS3.views which
explains how to write just such a view. """


class S3(object):
  def __init__(self, bucket, boto_3_client=None):
    # bucket can be a bucket name or a bucket config. boto_3_client can be
    # overridden for the sake of tests.
    self.bucket_config = get_bucket_config(bucket)
    self.boto_3_client = boto_3_client or get_boto_3_client(bucket)
    if 'manage.py' in sys.argv and 'test' in sys.argv and not boto_3_client:
      raise Exception(
          'You should use a mock boto3 client in unit tests so your tests do '
          'not attempt to contact Amazon servers because that could slow your '
          'tests down and put test files on Amazon servers.')

  def list(self):
    """ [('blahblahblah.jpg', datetime(2018, 6, 28, 21)),
         (file name, last modified)] """
    to_return = []
    # You don't have to can_read_net here. __init__ forces tests to pass in an
    # s3_override, and  dev and stage use the dev s3 buckets.
    lookup_result = self._s3.list_objects_v2(Bucket=self._bucket)
    # If the bucket_name is empty they omit the Contents entirely.
    if 'Contents' in lookup_result:
      for obj in lookup_result['Contents']:
        to_return.append((obj['Key'], obj['LastModified']))
    return to_return

  def download(self, file_name, local_file_name=None):
    local_file_name = local_file_name or file_name
    self._s3.download_file(self._bucket, file_name, local_file_name)

  def rm_download(self, local_file_name):
    os.remove(local_file_name)

  def image_bytes(self, file_name):
    """
    return HttpResponse(S3().image_bytes(file_name), content_type='image/jpeg')
    """
    if re.compile(r'[\/\\]').search(file_name):
      raise Exception(
          'I\'m expecting simply a file_name I can download, '
          'not a path to a file that\'s already downloaded.')
    for tries in range(3):
      if not os.path.exists(file_name):  # More or less always.
        # This throws an exception if the file doesn't exist on S3.
        self.download(file_name)
      # So if we get here, we know the file exists on S3. So far so good. But
      # one time, this open call here triggered a FileNotFoundError. Now, I
      # could see that happening if somebody opens a pile of tabs that all try
      # to load this image at once, and then there's a race where
      # os.path.exists at first but then before open gets called, a different
      # thread runs os.remove. My answer is to take 3 tries to load an image.
      try:
        f = open(file_name, 'rb')
      except FileNotFoundError:
        continue
      read = f.read()
      f.close()
      self.rm_download(file_name)
      return read
    log_error('Never able to download and read an image', (
        'I tried 3 times to download and read {}').format(file_name))

  def utf8_encoded_image(self, file_name):
    return base64.b64encode(self.image_bytes(file_name)).decode('utf-8')

  def upload(self, file_name, remote_file_name=None):
    remote_file_name = remote_file_name or file_name
    self._s3.upload_file(file_name, self._bucket, remote_file_name)

  def delete(self, file_name):
    """ Regardless of whether file_name exists or not in the bucket, this will
    return a 204. """
    got = self._s3.delete_object(Bucket=self._bucket, Key=file_name)
    return got['ResponseMetadata']['HTTPStatusCode'] == 204

  def generate_presigned_post(self, file_name, file_type):
    SignedFile.objects.get_or_create(
        file_name=file_name, bucket_name=self.bucket_name)
    fields = {'Content-Type': file_type}
    conditions = [{'Content-Type': file_type}]
    """
    OK, so if my latest comment is correct, and this isn't necessary, then I
    can just remove this entirely.
    if not self.sensitive:
      # I could have sworn this used to work, but now it doesn't seem to. It's
      # not until you also add an S3 -> your bucket_name -> security ->
      # bucket policy that it becomes possible to publically read stuff out of
      # a bucket_name.
      fields['acl'] = 'public-read'
      conditions.insert(0, {'acl': 'public-read'})
    """
    return self._s3.generate_presigned_post(
        Bucket=self._bucket,
        Key=file_name,
        Fields=fields,
        Conditions=conditions,
        ExpiresIn=3600)


class SignedFile(models.Model):
  """ In order to upload a file, your server must first sign it. djaveS3 takes
  that opportunity to keep track of all the files that get signed and uploaded
  so it can circle back around later and delete anything that didn't end up in
  the Files table, which is the list of files that are actually getting used
  for anything. """
  file_name = models.CharField(max_length=200)
  bucket_name = models.CharField(max_length=200)
  created_at = models.DateTimeField(auto_now_add=True)

  def delete_file(self):
    boto3_client.delete(self.file_name)

  def __repr__(self):
    return '<SignedFile {}: {}>'.format(self.pk, self.file_name)
