from django.http import JsonResponse, HttpResponse, Http404
from django.shortcuts import render


from djaveS3.get_bucket import get_bucket

from djaveS3.s3 import S3
from djaveS3.file_types import (
    suffix_from_file_type, content_type_from_file_name)
from djaveS3.random_string import random_string


def sensitive_image_response(bucket, file_name):
  """ This function is helpful to construct your own views that will return the
  actual bytes for a sensitive image. You need to pass the literal bytes for
  sensitive photos through your server in order to put security checks in front
  of those bytes. So for instance you might put something like this in your
  views.py:

  def view_photo_of_steve(request, file_name):
    if request.user.username != 'Steve':
      raise Exception('Only Steve may look at photos of Steve!')
    return sensitive_image_response('steves_s3_bucket', file_name)

  def steves_page(request):
    return render(
        request, 'steve.html', {'steve_photo_url': reverse(
            'view_photo_of_steve',
            kwargs={'file_name': StevePhoto.objects.first().file_name})})

  And something like this in steve.html or whatever

  <img src="{{ steve_photo_url }}">
  """
  actual_bucket = get_bucket(bucket)
  if actual_bucket.public:
    raise Exception((
        'S3 bucket {} is public, so performance-wise, it is best to just '
        'leave this server out of it entirely and use public_photo_url '
        'in djaveS3.S3 instead.').format(bucket))
  img_bytes = S3(bucket).image_bytes(file_name)
  if img_bytes:
    return HttpResponse(
        img_bytes, content_type=content_type_from_file_name(file_name))
  return Http404()


def photo_demo(request):
  """ This simple page is what I'm using to get photo management working. """
  return render(request, 'photo_demo.html', {})


def sign_s3_sensitive(request):
  return sign_s3(request, sensitive=True)


def sign_s3_public(request):
  return sign_s3(request, sensitive=False)


def sign_s3(request, sensitive):
  """ The user is about to try to upload a photo directly to S3. We gotta
  sign it and say where it goes. """
  file_type = request.GET.get('file_type', '')
  if not file_type:
    return HttpResponse(
        'You have to include a file_type parameter.', status=400)
  suffix = suffix_from_file_type(file_type)
  if not suffix:
    # If you're figuring out what to do with an exception like this,
    # go modify set_up_file_upload in
    # id_verify/templates/verify_my_id_script.html
    raise Exception(
        'Not sure what to do with file_type {}'.format(file_type))

  destination_file_name = '{}.{}'.format(random_string(), suffix)
  presigned_post = S3(sensitive=sensitive).generate_presigned_post(
      destination_file_name, file_type)

  return JsonResponse({
      'presigned_post': presigned_post,
      'destination_file_name': destination_file_name})
