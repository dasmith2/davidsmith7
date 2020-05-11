# Put settings that are particular to this specific site here instead of in
# settings.py


# Amazon S3 test buckets. Replace these!
from djaveS3.bucket_config import BucketConfig
MAX_WIDTH_OR_HEIGHT = 800
IAM_ACCESS_KEY_ID = 'AKIAXKZEWKA3E4O4VCM6'
IAM_SECRET_ACCESS_KEY = 'MrJnXwk83JbFXDyzHOcLzCyywq3Moeek0g72dN9N'
PUBLIC_BUCKET_NAME = 'davespacepublic'
PUBLIC_BUCKET = BucketConfig(
    PUBLIC_BUCKET_NAME, IAM_ACCESS_KEY_ID,
    IAM_SECRET_ACCESS_KEY, is_public=True,
    max_width_or_height=MAX_WIDTH_OR_HEIGHT)
PRIVATE_BUCKET_NAME = 'davespaceprivate'
PRIVATE_BUCKET = BucketConfig(
    PRIVATE_BUCKET_NAME, IAM_ACCESS_KEY_ID,
    IAM_SECRET_ACCESS_KEY, is_public=False,
    max_width_or_height=MAX_WIDTH_OR_HEIGHT)
S3_BUCKETS = [PRIVATE_BUCKET, PUBLIC_BUCKET]
