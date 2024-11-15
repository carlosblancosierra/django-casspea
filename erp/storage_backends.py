from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage

class StaticStorage(S3Boto3Storage):
    location = 'static'
    default_acl = 'public-read'

    def __init__(self, *args, **kwargs):
        print("StaticStorage: Initializing")
        super().__init__(*args, **kwargs)

class MediaStorage(S3Boto3Storage):
    location = 'media'
    default_acl = 'public-read'
    file_overwrite = False

    def __init__(self, *args, **kwargs):
        print("MediaStorage: Initializing")
        super().__init__(*args, **kwargs)

    def _save(self, name, content):
        print(f"MediaStorage: Attempting to save file: {name}")
        try:
            result = super()._save(name, content)
            print(f"MediaStorage: Successfully saved file: {name}")
            return result
        except Exception as e:
            print(f"MediaStorage: Error saving file {name}: {str(e)}")
            raise

    def url(self, name):
        print(f"Getting URL for file: {name}")
        return super().url(name)
