from django.contrib import admin

# Register your models here.

from .models import Plan, UserProfile, ThumbSize
# Register your models here.
admin.site.register(Plan)
admin.site.register(UserProfile)
admin.site.register(ThumbSize)
