from django.contrib import admin

# Register your models here.
from .models import ImageSet, UploadedImage, TimedImageLink
# Register your models here.
admin.site.register(ImageSet)
admin.site.register(UploadedImage)
admin.site.register(TimedImageLink)
