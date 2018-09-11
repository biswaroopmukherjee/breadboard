from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate
from api import views



class DatasetTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username='jacob', email='jacob@mit.edu', password='top_secret')

    def test_dataset_get(self):
        # get all datasets
        request = self.factory.get('/datasets/')
        force_authenticate(request, user=self.user, token=self.user.auth_token)
        view = views.DatasetViewSet.as_view({'get':'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)

    def test_dataset_post(self):
        # Create a dataset
        request = self.factory.post('/datasets/', {'name': 'new data'})
        force_authenticate(request, user=self.user, token=self.user.auth_token)
        view = views.DatasetViewSet.as_view({'post':'create'})
        response = view(request)
        self.assertEqual(response.status_code, 201)




class ImageTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username='jacob', email='jacob@mit.edu', password='top_secret')

    def test_image_get(self):
        # get all images
        request = self.factory.get('/images/')
        force_authenticate(request, user=self.user, token=self.user.auth_token)
        view = views.ImageViewSet.as_view({'get':'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)

    def test_image_post(self):
        # Create an image
        request = self.factory.post('/images/',{'name': 'testimg', 'lab':'bec1'})
        force_authenticate(request, user=self.user, token=self.user.auth_token)
        view = views.ImageViewSet.as_view({'post':'create'})
        response = view(request)
        self.assertEqual(response.status_code, 201)
