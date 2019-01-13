import time

from django.shortcuts import render
from rest_framework import viewsets
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.generics import CreateAPIView
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from django.core.signals import request_finished, request_started
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from api.serializers import (
                GroupSerializer,
                UserSerializer,
                UserProfileSerializer,
                ImageSerializerList,
                ImageSerializerDetail,
                CameraSerializer,
                RunSerializerList,
                RunSerializerDetail,
                DatasetSerializer,
                ProjectSerializer,
                LabSerializer
        )

from api.models import UserProfile, Image, Camera, Run, Dataset, Project, Lab



class CreateUserView(CreateAPIView):

    model = User
    permission_classes = [
        permissions.AllowAny # Or anon users can't register
    ]
    serializer_class = UserSerializer


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
