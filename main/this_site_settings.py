from djaveS3.bucket_config import BucketConfig


# Amazon S3
IAM_ACCESS_KEY_ID = 'AKIAXKZEWKA3E4O4VCM6'
IAM_SECRET_ACCESS_KEY = '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'
PUBLIC_BUCKET = BucketConfig(
    'davespacepublic', IAM_ACCESS_KEY_ID,
    IAM_SECRET_ACCESS_KEY, is_public=True)
PRIVATE_BUCKET = BucketConfig(
    'davespaceprivate', IAM_ACCESS_KEY_ID,
    IAM_SECRET_ACCESS_KEY, is_public=False)
BUCKETS = [PRIVATE_BUCKET, PUBLIC_BUCKET]
