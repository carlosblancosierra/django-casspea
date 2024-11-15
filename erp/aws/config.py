import environ
from storages.backends.s3boto3 import S3Boto3Storage

# Initialize environ
env = environ.Env()

class AWSConfig:
    """AWS Configuration Class"""

    # Storage Classes
    class StaticStorage(S3Boto3Storage):
        """Storage class for static files"""
        location = 'static'
        default_acl = 'public-read'
        file_overwrite = True

    class MediaStorage(S3Boto3Storage):
        """Storage class for media files"""
        location = 'media'
        default_acl = 'public-read'
        file_overwrite = False

    class PrivateMediaStorage(S3Boto3Storage):
        """Storage class for private media files"""
        location = 'private'
        default_acl = 'private'
        file_overwrite = False
        custom_domain = False

    def __init__(self):
        # AWS Credentials
        self.AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID', default='')
        self.AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY', default='')
        self.AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME', default='')
        self.AWS_S3_REGION_NAME = env('AWS_S3_REGION_NAME', default='eu-west-2')
        self.AWS_S3_CUSTOM_DOMAIN = f'{self.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'

        # S3 Settings
        self.AWS_DEFAULT_ACL = None
        self.AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
        self.AWS_QUERYSTRING_AUTH = False
        self.AWS_S3_FILE_OVERWRITE = False

        # Storage Configuration
        self.USE_S3 = env.bool('USE_S3', default=Tru)
        self.STATICFILES_STORAGE = 'erp.aws.aws.AWSConfig.StaticStorage'
        self.DEFAULT_FILE_STORAGE = 'erp.aws.aws.AWSConfig.MediaStorage'
        self.PRIVATE_FILE_STORAGE = 'erp.aws.aws.AWSConfig.PrivateMediaStorage'
        self.STATIC_URL = f'https://{self.AWS_S3_CUSTOM_DOMAIN}/static/'
        self.MEDIA_URL = f'https://{self.AWS_S3_CUSTOM_DOMAIN}/media/'

# Create single instance to export
aws_config = AWSConfig()
