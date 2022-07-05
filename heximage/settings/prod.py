""" Production Settings """

import os
# import dj_database_url
from .dev import *

from storages.backends.s3boto3 import S3Boto3Storage

class MediaStorage(S3Boto3Storage):
    location = 'media'
    file_overwrite = False

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'mysite/static'),
]

############
# DATABASE #
############
# DATABASES = {
#     'default': dj_database_url.config(
#         default=os.getenv('DATABASE_URL')
#     )
# }



AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}





############
# SECURITY #
############

DEBUG = False # bool(os.getenv('DJANGO_DEBUG', ''))

ALLOWED_HOSTS = ['*']
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
AWS_LOCATION = 'static'
AWS_S3_CUSTOM_DOMAIN = env('AWS_S3_CUSTOM_DOMAIN')
# Depending on the AWS account used, you might also need to declare AWS_SESSION_TOKEN as an environment variable
DEFAULT_FILE_STORAGE = 'mysite.storage_backends.MediaStorage'
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
STATIC_URL = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, AWS_LOCATION)
