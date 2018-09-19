from django.shortcuts import render
from rest_framework import viewsets
from django.contrib.auth.models import User, Group
from rest_framework import permissions
from rest_framework.generics import CreateAPIView
from rest_framework.exceptions import ParseError


from api.serializers import (
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

class ImageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows images to be viewed or edited
    """
    serializer_class = ImageSerializer
    def get_queryset(self):
        """
        Restricts queries by lab and/or
        workday and/or a datetime range """
        queryset = Image.objects.all()
        filter_dirty = {
            'run__lab__name' : self.request.query_params.get('lab', None),
            'run__workday' : self.request.query_params.get('workday', None),
            'created__range' : (
                        self.request.query_params.get('start_datetime', None),
                        self.request.query_params.get('end_datetime', None),
                        ),
        }
        filter_clean = {k: v for k, v in filter_dirty.items() if not (
                        v==None or
                        (isinstance(v, tuple) and (None in v))
                )}

        if len(filter_clean) is not 0:
            queryset = queryset.filter(**filter_clean)
        return queryset


class RunViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows runs to be viewed or edited
    """
    serializer_class = RunSerializer
    def get_queryset(self):
        """
        Restricts queries by lab and/or
        workday and/or a datetime range """
        queryset = Run.objects.all()
        filter_dirty = {
            'lab__name' : self.request.query_params.get('lab', None),
            'workday' : self.request.query_params.get('workday', None),
            'workday__range' : (
                        self.request.query_params.get('start_date', None),
                        self.request.query_params.get('end_date', None),
                        ),
            'runtime__range' : (
                        self.request.query_params.get('start_datetime', None),
                        self.request.query_params.get('end_datetime', None),
                        ),
        }
        filter_clean = {k: v for k, v in filter_dirty.items() if not (
                        v==None or
                        (isinstance(v, tuple) and (None in v))
                )}

        if len(filter_clean) is not 0:
            queryset = queryset.filter(**filter_clean)
        return queryset




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
