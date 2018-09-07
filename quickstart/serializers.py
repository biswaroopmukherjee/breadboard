from django.contrib.auth.models import User, Group
from rest_framework import serializers
from quickstart.models import (
        Image, Camera, Run, Dataset,
        Project, Lab, UserProfile
        )

class UserSerializer(serializers.HyperlinkedModelSerializer):
    userprofile = serializers.HyperlinkedRelatedField(
        queryset = UserProfile.objects.all(),
        many=False,
        view_name='userprofile-detail'
    )
    class Meta:
        model = User
        fields = ('url', 'id', 'username', 'email', 'groups', 'userprofile')


class UserProfileSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HyperlinkedRelatedField(
        queryset = User.objects.all(),
        many=False,
        view_name='user-detail'
    )
    class Meta:
        model = UserProfile
        fields = ('url', 'id', 'user', 'lab', 'description')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'id', 'name')

class ImageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Image
        fields = ('url', 'id','name', 'created', 'notes', 'filepath', 'tags',
                    'cropi', 'atom', 'odpath', 'total_atoms',
                    'atomsperpixel', 'thumbnail', 'run', 'camera')

class CameraSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Camera
        fields = ('url', 'id','name', 'sdk_id', 'created', 'magnification', 'axis',
                    'pixel_size', 'double_imaging', 'active',
                    'calibration_dataset' )

class RunSerializer(serializers.HyperlinkedModelSerializer):
    images = serializers.HyperlinkedRelatedField(
        queryset = Image.objects.all(),
        view_name='image-detail',
        many=True
    )
    class Meta:
        model = Run
        fields = ('url', 'id','created', 'runtime', 'parameters', 'bad_shot',
                    'lab', 'dataset', 'images')

class DatasetSerializer(serializers.HyperlinkedModelSerializer):
    runs = serializers.HyperlinkedRelatedField(
        queryset = Run.objects.all(),
        view_name='run-detail',
        many=True
    )

    class Meta:
        model = Dataset
        fields = ('url', 'id','name', 'created', 'notes',
                'flag', 'tags', 'project', 'lab',
                'runs')

class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    datasets = serializers.HyperlinkedRelatedField(
        queryset = Dataset.objects.all(),
        view_name='dataset-detail',
        many=True
    )
    class Meta:
        model = Project
        fields = ('url', 'id','name', 'created', 'notes', 'lab', 'datasets')

class LabSerializer(serializers.HyperlinkedModelSerializer):
    projects = serializers.HyperlinkedRelatedField(
        queryset = Project.objects.all(),
        view_name='project-detail',
        many=True
    )
    userprofiles = serializers.HyperlinkedRelatedField(
        queryset = UserProfile.objects.all(),
        view_name='userprofile-detail',
        many=True
    )
    class Meta:
        model = Lab
        fields = ('url', 'id','name', 'created', 'info', 'photo', 'runs', 'projects', 'userprofiles')
