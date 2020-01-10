from django.test import TestCase
from django.contrib.auth.models import User
from api.models import Lab, Run, Image, Dataset
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate
from api import views



class DatasetTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username='jacob', email='jacob@mit.edu', password='top_secret')
        self.lab = Lab.objects.create(name='newlab')
        self.run = Run.objects.create(lab=self.lab)
        self.dataset = Dataset.objects.create(name='test_dataset', lab=self.lab)
        self.run.dataset = self.dataset
        self.run.save()

    def test_dataset_get(self):
        # get all datasets
        request = self.factory.get('/datasets/')
        force_authenticate(request, user=self.user, token=self.user.auth_token)
        view = views.DatasetViewSet.as_view({'get':'list'})
        response = view(request)
        # print(response.data)
        self.assertEqual(response.status_code, 200)

    def test_dataset_post(self):
        # Create a dataset
        request = self.factory.post('/datasets/', {'name': 'new data'})
        force_authenticate(request, user=self.user, token=self.user.auth_token)
        view = views.DatasetViewSet.as_view({'post':'create'})
        response = view(request)
        self.assertEqual(response.status_code, 201)

    def test_add_to_dataset(self):
        # test adding a run to the dataset
        runobj = {
            'dataset': '1',
            'parameters': {"TOF":0, "evap":90}
        }
        request = self.factory.put('/runs/1/', runobj, format='json')
        force_authenticate(request, user=self.user, token=self.user.auth_token)
        view = views.RunViewSet.as_view({'put':'update'})
        response = view(request, pk='1')
        # print(response.data)
        # print(response.status_code)
        self.assertEqual(response.status_code, 200)


class LabTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username='jacob', email='jacob@mit.edu', password='top_secret')

    def test_lab_get(self):
        # get all Labs
        request = self.factory.get('/labs/')
        force_authenticate(request, user=self.user, token=self.user.auth_token)
        view = views.LabViewSet.as_view({'get':'list'})
        response = view(request)
        ##print(response.data)
        self.assertEqual(response.status_code, 200)

    def test_lab_post(self):
        # Create a Lab
        request = self.factory.post('/labs/', {'name': 'newlab'})
        force_authenticate(request, user=self.user, token=self.user.auth_token)
        view = views.LabViewSet.as_view({'post':'create'})
        response = view(request)
        self.assertEqual(response.status_code, 201)


class RunTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username='jacob', email='jacob@mit.edu', password='top_secret')

    def test_run_get(self):
        # get all Runs
        request = self.factory.get('/runs/')
        force_authenticate(request, user=self.user, token=self.user.auth_token)
        view = views.RunViewSet.as_view({'get':'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)

    def test_run_post(self):
        # Create a Run
        runobj = {
                'parameters': {"TOF":0, "evap":9}
                }
        request = self.factory.post('/runs/', runobj, format='json')
        force_authenticate(request, user=self.user, token=self.user.auth_token)
        view = views.RunViewSet.as_view({'post':'create'})
        response = view(request)
        self.assertEqual(response.status_code, 201)



class ImageTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username='jacob', email='jacob@mit.edu', password='top_secret')
        self.lab = Lab.objects.create(name='newlab')
        self.run = Run.objects.create(lab=self.lab)
        self.image = Image.objects.create(name='newimage', lab=self.lab)
        


    def test_image_get(self):
        # get all images
        request = self.factory.get('/images/')
        force_authenticate(request, user=self.user, token=self.user.auth_token)
        view = views.ImageViewSet.as_view({'get':'list'})
        response = view(request)
        result = response.data.get('results')[0]
        self.assertEqual(result.get('name'), self.image.name)
        self.assertEqual(response.status_code, 200)


    def test_image_post(self):
        # Create an image
        img = {
            'names':'2019-03-04_15-10-06_SensicamQE,2019-03-04_15-10-37_SensicamQE',
            'lab':'newlab',
            'created':'2019-03-04T15:10:06Z,2019-03-04T15:10:37Z'
            }
        request = self.factory.post('/images/',img)
        force_authenticate(request, user=self.user, token=self.user.auth_token)
        view = views.ImageViewSet.as_view({'post':'create'})
        response = view(request)
        # result = response.data.get('results')[0]
        self.assertEqual(response.status_code, 200)


    def test_image_post_force_match(self):
        # Create an image
        img = {
            'names':self.image.name,
            'lab':'newlab',
            'created':self.image.created,
            'force_match': 'True'
            }
        request = self.factory.post('/images/',img)
        force_authenticate(request, user=self.user, token=self.user.auth_token)
        view = views.ImageViewSet.as_view({'post':'create'})
        response = view(request)
        result = response.data.get('results')[0]
        # print(result)
        self.assertEqual(result.get('name'), self.image.name)
        self.assertEqual(response.status_code, 200)