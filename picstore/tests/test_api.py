import json
import shutil
import tempfile
import datetime
from PIL import Image
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from django.test import override_settings
from picstore.api.views import ImageSetAPIView, CreateLinkAPIView, RestrictedTimeView
from picstore.models import ImageSet, UploadedImage, TimedImageLink
from accounts.models import Plan, ThumbSize, UserProfile


MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestImageSetAPIView(APITestCase):

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
        test_set = ImageSet.objects.create(
            author=cls.test_user1
        )
        test_set_2 = ImageSet.objects.create(
            author=cls.test_user2
        )
        cls.test_image_path = 'picstore/tests/test_image/dino.jpg'
        cls.test_image = open(cls.test_image_path, 'rb')
        cls.simple_file_image = SimpleUploadedFile(name="testimage.jpg",  content=open(
            cls.test_image_path, 'rb').read(), content_type='image/jpeg')
        test_set.create_images(cls.simple_file_image)
        test_set_2.create_images(cls.simple_file_image)
        cls.client = APIClient()
        test_gif_image_path = 'picstore/tests/test_image/dino.gif'
        cls.test_gif_image = open(test_gif_image_path, 'rb')

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_access_no_auth(self):
        response = self.client.get('/api/',)
        self.assertEquals(response.status_code, 403)

    def test_access_w_auth(self):
        self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get('/api/',)
        self.assertEquals(response.status_code, 200)

    def test_get_response(self):
        self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get('/api/',)
        self.assertEquals(len(json.loads(response.content)['results']), 1)
        self.assertEquals(len(json.loads(response.content)
                          ['results'][0]['files']), 1)
        self.assertEquals(json.loads(response.content)[
                          'results'][0]['files'][0]['size'], '200px')

    def test_get_if_multiple_created(self):
        self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get('/api/',)
        self.assertEquals(len(json.loads(response.content)['results']), 1)
        self.assertEquals(len(json.loads(response.content)
                          ['results'][0]['files']), 3)
        self.assertEquals(json.loads(response.content)[
                          'results'][0]['files'][0]['size'], '1352 x 548px')
        self.assertEquals(json.loads(response.content)[
                          'results'][0]['files'][1]['size'], '200px')
        self.assertEquals(json.loads(response.content)[
                          'results'][0]['files'][2]['size'], '400px')

    def test_get_if_original_created(self):
        self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get('/api/',)
        self.assertEquals(json.loads(response.content)[
                          'results'][0]['files'][0]['size'], '1352 x 548px')
        self.assertEquals(json.loads(response.content)[
                          'results'][0]['files'][0]['is_original'], True)

    def test_post_success(self):
        self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        test_image = open(self.test_image_path, 'rb')
        response = self.client.post('/api/', {'file': test_image})
        self.assertEquals(json.loads(response.content), {
                          'detail': 'Thumbnails have been created!'})
        self.assertEquals(response.status_code, 200)
        self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get('/api/',)
        self.assertEquals(len(json.loads(response.content)['results']), 2)

    def test_post_successsds(self):
        self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.post('/api/', {'file': self.test_gif_image})
        expected_response = {
            'file': ['Only .jpg and .png file formats are allowed']}
        self.assertEquals(json.loads(response.content), expected_response)

    @override_settings(MAX_FILE_SIZE=100)
    def test_posst_success(self):
        self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.post('/api/', {'file': self.test_image})
        self.assertEquals(json.loads(response.content), {
                          'file': ['File size too big!']})
        self.assertEquals(response.status_code, 400)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestCreateLinkAPIView(APITestCase):

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
        test_set = ImageSet.objects.create(
            author=cls.test_user1
        )
        test_set_2 = ImageSet.objects.create(
            author=cls.test_user2
        )
        test_image_path = 'picstore/tests/test_image/dino.jpg'
        cls.test_image = open(test_image_path, 'rb')
        cls.simple_file_image = SimpleUploadedFile(name="testimage.jpg",  content=open(
            test_image_path, 'rb').read(), content_type='image/jpeg')
        test_set.create_images(cls.simple_file_image)
        test_set_2.create_images(cls.simple_file_image)
        cls.client = APIClient()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_access_no_auth(self):
        response = self.client.get('/api/create/',)
        self.assertEquals(response.status_code, 403)

    def test_access_w_auth(self):
        self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get('/api/create/',)
        self.assertEquals(response.status_code, 405)

    def test_access_w_auth(self):
        self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        post_data = {
            'image': 1,
            'delta': 300
        }
        response = self.client.post('/api/create/', data=post_data)
        self.assertEquals(response.status_code, 200)

    def test_expiry_date_calculated(self):
        self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        post_data = {
            'image': 1,
            'delta': 300
        }
        creation_time = timezone.now()
        response = self.client.post('/api/create/', post_data, format="json")
        expected_response = timezone.now() + datetime.timedelta(seconds=300)
        expected_response = expected_response.strftime('%Y/%m/%d - %H:%M:%S')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(json.loads(response.content)[
                          'expiry date'], expected_response)

    def test_access_to_foreign_thumbnail(self):
        self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        post_data = {
            'image': 3,
            'delta': 300
        }
        response = self.client.post('/api/create/', post_data, format="json")
        self.assertEquals(json.loads(response.content), {
                          "image": ["Access Restricted"]})
        self.assertEquals(response.status_code, 400)

    def test_link_creation_thumbnail_doesnt_exist(self):
        self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        post_data = {
            'image': 8,
            'delta': 300
        }
        response = self.client.post('/api/create/', post_data, format="json")
        self.assertEquals(json.loads(response.content), {
                          'image': ["Image of that id doesn't exist"]})
        self.assertEquals(response.status_code, 400)

    def test_link_creation_too_small_delta(self):
        self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        post_data = {
            'image': 1,
            'delta': 30
        }
        response = self.client.post('/api/create/', post_data, format="json")
        self.assertEquals(json.loads(response.content), {
                          'delta': ['Ensure this value is greater than or equal to 300.']})
        self.assertEquals(response.status_code, 400)

    def test_link_creation_too_big_delta(self):
        self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        post_data = {
            'image': 1,
            'delta': 300000000
        }
        response = self.client.post('/api/create/', post_data, format="json")
        self.assertEquals(json.loads(response.content), {
                          'delta': ['Ensure this value is less than or equal to 30000.']})
        self.assertEquals(response.status_code, 400)

    def test_access_after_expiry(self):
        self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        post_data = {
            'image': 1,
            'delta': 300
        }
        creation_time = timezone.now()
        response = self.client.post('/api/create/', post_data, format="json")
        URI = json.loads(response.content)['URI']
        uuid = URI.split('/')[-2]
        response = self.client.get(URI)
        self.assertEquals(response.status_code, 200)
        instance = TimedImageLink.objects.get(id=uuid)
        instance.expire_by_date = timezone.now() - datetime.timedelta(seconds=10)
        instance.save()
        response = self.client.get(URI)
        self.assertEquals(response.status_code, 403)
