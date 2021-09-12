import shutil
import tempfile
import datetime
from PIL import Image
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APIRequestFactory, APITestCase, APIClient
from django.test import override_settings
from picstore.api.views import ImageSetAPIView, CreateLinkAPIView, RestrictedTimeView
from picstore.models import ImageSet, UploadedImage, TimedImageLink
from accounts.models import Plan, ThumbSize, UserProfile

MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestImageSetModel(APITestCase):

    @classmethod
    def setUpTestData(cls):

        cls.test_user1 = User.objects.create_user(
            username='testuser1', password='1X<ISRUkw+tuK')
        cls.test_user2 = User.objects.create_user(
            username='testuser2', password='2HJ1vRV0Z&3iD')
        thumb_original = ThumbSize.objects.create(
            height=0,
        )
        thumb_200 = ThumbSize.objects.create(
            height=200,
        )
        thumb_400 = ThumbSize.objects.create(
            height=400,
        )
        plan_basic = Plan.objects.create(
            title='Basic',
        )
        plan_basic.thumb_sizes.add(thumb_200)
        plan_premium = Plan.objects.create(
            title='Premium',
            enable_original_image=True,
        )
        plan_premium.thumb_sizes.add(thumb_200)
        plan_premium.thumb_sizes.add(thumb_400)

        plan_enterprise = Plan.objects.create(
            title='Enterprise',
            enable_original_image=True,
            enable_expiring_link=True
        )
        plan_enterprise.thumb_sizes.add(thumb_200)
        plan_enterprise.thumb_sizes.add(thumb_400)

        test_user1_userprofile = UserProfile.objects.create(
            user=cls.test_user1,
            plan=plan_basic
        )

        test_user2_userprofile = UserProfile.objects.create(
            user=cls.test_user2,
            plan=plan_enterprise
        )
        cls.test_set = ImageSet.objects.create(
            author=cls.test_user1
        )
        cls.test_set_2 = ImageSet.objects.create(
            author=cls.test_user2
        )
        cls.test_image_path = 'picstore/tests/test_image/dino.jpg'
        cls.test_image = open(cls.test_image_path, 'rb')
        cls.simple_file_image = SimpleUploadedFile(name="testimage.jpg",  content=open(
            cls.test_image_path, 'rb').read(), content_type='image/jpeg')


    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_creates_images(self):
        self.assertEquals(UploadedImage.objects.count(), 0)
        self.test_set.create_images(self.simple_file_image)
        self.assertEquals(UploadedImage.objects.count(), 1)

    def test_creates_images_according_to_plan(self):
        self.assertEquals(UploadedImage.objects.count(), 0)
        self.test_set_2.create_images(self.simple_file_image)
        self.assertEquals(UploadedImage.objects.count(), 3)

    def test_creates_images_resizes(self):
        self.test_set_2.create_images(self.simple_file_image)
        im = Image.open(self.test_set_2.images.all()[0].file)
        im2 = Image.open(self.test_set_2.images.all()[1].file)
        self.assertEquals(im.width, 1352)
        self.assertEquals(im.height, 548)
        self.assertEquals(im2.width, 493)
        self.assertEquals(im2.height, 200)
