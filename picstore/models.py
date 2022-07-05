import os
import uuid
import random
import string
import io
import sys
from django.db import models
from django.db.models.signals import post_delete, pre_delete
from django.utils import timezone
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.validators import FileExtensionValidator
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.dispatch import receiver
from PIL import Image
from accounts.models import ThumbSize


class ImageSet(models.Model):
    author = models.ForeignKey(
        'auth.User', on_delete=models.CASCADE, related_name='imagesets')

    class Meta:
        verbose_name_plural = "Image Sets"
        ordering = ['id']

    def __str__(self):
        return ('Image Set({}) {}'.format(self.id, self.author))

    def create_images(self, file):
        charchoices = string.ascii_uppercase + string.ascii_lowercase + string.digits
        name, ext = os.path.splitext(file.name)
        format_ext_dict = {'.jpg': 'JPEG', '.png': 'PNG'}
        img_format = format_ext_dict[ext]
        if self.author.userprofile.plan.enable_original_image:

            im = Image.open(file)
            im_io = io.BytesIO()
            im.save(im_io, format=img_format)

            image = UploadedImage.objects.create(
                set=self,
                is_original=True,
                size=ThumbSize.objects.get(height=0)
            )
            filename = name + '_original_' + \
                ''.join(random.choices(charchoices, k=10))
            imagefilename = filename + ext
            image.file.save(imagefilename, ContentFile(
                im_io.getvalue()), save=False)
            image.save()

        for size in self.author.userprofile.plan.thumb_sizes.all():
            im = Image.open(file)
            filesize = (im.width, size.height)

            if im.height > size.height:
                im.thumbnail(filesize, Image.ANTIALIAS)
                im_io = io.BytesIO()
                im.save(im_io, format=img_format)
                image = UploadedImage.objects.create(
                    set=self,
                    size=size,
                )
                filesize = (im.width, im.height)
                filename = name + f'_{filesize[0]}x{filesize[1]}_' +  \
                    ''.join(random.choices(charchoices, k=10))
                imagefilename = filename + ext
                image.file.save(imagefilename, ContentFile(
                    im_io.getvalue()), save=False)
                image.save()


def user_directory_path(instance, filename):
    return 'upload/{0}/{1}'.format(instance.set.author, filename)


class UploadedImage(models.Model):
    set = models.ForeignKey('picstore.ImageSet',
                            on_delete=models.CASCADE, related_name='images')

    file = models.ImageField(upload_to=user_directory_path, validators=[
        FileExtensionValidator(allowed_extensions=['jpg', 'png'])])

    size = models.ForeignKey('accounts.ThumbSize', on_delete=models.CASCADE)
    is_original = models.BooleanField(default=False)

    def __str__(self):
        if self.is_original:
            return '{} (original)'.format(self.file.name.split('/')[-1])
        else:

            return '{} (height - {}px)'.format(self.file.name.split('/')[-1], self.size)

    class Meta:
        verbose_name_plural = "User Images"
        ordering = ['id']

@receiver(pre_delete, sender=UploadedImage)
def delete_image_hook(sender, instance, using, **kwargs):
    instance.file.delete()


class TimedImageLink(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    image = models.ForeignKey('picstore.UploadedImage',
                              on_delete=models.CASCADE)
    expire_by_date = models.DateTimeField()

    def __str__(self):
        return '{}, expiring on {}'.format(
            self.image, self.expire_by_date.strftime('%Y/%m/%d - %H:%M'))

    class Meta:
        verbose_name_plural = "Time Restricted Links"
        ordering = ['-id']
        indexes = [
            models.Index(fields=['-id',]),
]
