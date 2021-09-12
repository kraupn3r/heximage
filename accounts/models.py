from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="userprofile"
    )

    plan = models.ForeignKey('accounts.Plan', on_delete=models.PROTECT)

    def __str__(self):
        return self.user.username

class Plan(models.Model):
    title = models.CharField(max_length=40)
    enable_original_image = models.BooleanField(default=False)
    enable_expiring_link = models.BooleanField(default=False)
    thumb_sizes = models.ManyToManyField('accounts.ThumbSize')

    def __str__(self):
        return self.title

class ThumbSize(models.Model):
    height = models.PositiveIntegerField(unique=True)


    def __str__(self):
        return str(self.height)
