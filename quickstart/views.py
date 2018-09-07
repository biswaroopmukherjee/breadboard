from django.shortcuts import render
from rest_framework import viewsets
from django.contrib.auth.models import User, Group

from quickstart.serializers import (
                GroupSerializer,
                UserSerializer,
                UserProfileSerializer,
                ImageSerializer,
                CameraSerializer,
                RunSerializer,
                DatasetSerializer,
                ProjectSerializer,
                LabSerializer
        )

from quickstart.models import UserProfile, Image, Camera, Run, Dataset, Project, Lab


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer

class UserProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups of users to be viewed or edited
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

class ImageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows images to be viewed or edited
    """
    queryset = Image.objects.all()
    serializer_class = ImageSerializer


class RunViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows runs to be viewed or edited
    """
    queryset = Run.objects.all()
    serializer_class = RunSerializer

class CameraViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows cameras to be viewed or edited
    """
    queryset = Camera.objects.all()
    serializer_class = CameraSerializer

class DatasetViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups of runs (datasets) to be viewed or edited
    """
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer

class ProjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups of datasets (projects) to be viewed or edited
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

class LabViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups of users and datasets (labs) to be viewed or edited
    """
    queryset = Lab.objects.all()
    serializer_class = LabSerializer
