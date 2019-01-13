from django.contrib.auth.models import User, Group
from rest_framework import serializers
from api.models import (
        Image, Camera, Run, Dataset,
        Project, Lab, UserProfile
        )

class UserSerializer(serializers.ModelSerializer):
    userprofile = serializers.PrimaryKeyRelatedField(
        queryset = UserProfile.objects.all(),
        many=False,
        #view_name='userprofile-detail',
        allow_null=True,
        default=[],
    )
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):

        user = User.objects.create(
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()

        return user

    class Meta:
        model = User
        fields = ('url', 'id', 'username', 'password', 'email', 'groups', 'userprofile')


class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset = User.objects.all(),
        many=False,
        #view_name='user-detail',
        allow_null=True,
        default=[],
    )
    class Meta:
        model = UserProfile
        fields = ('url', 'id', 'user', 'lab', 'description')


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'id', 'name')

class CameraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera
        fields = ('url', 'id','name', 'sdk_id', 'created', 'magnification', 'axis',
                    'pixel_size', 'double_imaging', 'active', 'lab',
                    'calibration_dataset' )

class RunSerializerList(serializers.ModelSerializer):
    class Meta:
        model = Run
        fields = ('url', 'id','created', 'runtime', 'parameters', 'bad_shot',
                    'notes', 'workday','lab', 'dataset')

class RunSerializerDetail(serializers.ModelSerializer):
    images = serializers.HyperlinkedRelatedField(
        queryset = Image.objects.all(),
        view_name='image-detail',
        many=True,
        default=[],
    )
    class Meta:
        model = Run
        fields = ('url', 'id','created', 'runtime', 'parameters', 'bad_shot',
                    'notes', 'workday','lab', 'dataset', 'images')

class ImageSerializerList(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('url', 'id','name', 'created', 'notes', 'filepath', 'tags',
                    'cropi', 'atom', 'odpath', 'total_atoms', 'settings',
                    'atomsperpixel', 'thumbnail', 'run', 'camera')

class ImageSerializerDetail(serializers.ModelSerializer):
    run = RunSerializerDetail(many=False, read_only=True)
    class Meta:
        model = Image
        fields = ('url', 'id','name', 'created', 'notes', 'filepath', 'tags',
                    'cropi', 'atom', 'odpath', 'total_atoms', 'settings',
                    'atomsperpixel', 'thumbnail', 'run', 'camera', 'lab')


class DatasetSerializer(serializers.ModelSerializer):
    runs = serializers.PrimaryKeyRelatedField(
        queryset = Run.objects.all(),
        #view_name='run-detail',
        many=True,
        allow_null=True,
        default=[],
    )

    class Meta:
        model = Dataset
        fields = ('url', 'id','name', 'created', 'notes',
                'flag', 'tags', 'project', 'lab',
                'runs')

class ProjectSerializer(serializers.ModelSerializer):
    datasets = serializers.PrimaryKeyRelatedField(
        queryset = Dataset.objects.all(),
        #view_name='dataset-detail',
        many=True,
        allow_null=True,
        default=[],
    )
    class Meta:
        model = Project
        fields = ('url', 'id','name', 'created', 'notes', 'lab', 'datasets')

class LabSerializer(serializers.ModelSerializer):
    cameras = serializers.PrimaryKeyRelatedField(
        queryset = Camera.objects.all(),
        #view_name='camera-detail',
        many=True,
        allow_null=True,
        default=[],
    )
    projects = serializers.PrimaryKeyRelatedField(
        queryset = Project.objects.all(),
        #view_name='project-detail',
        many=True,
        allow_null=True,
        default=[],
    )
    userprofiles = serializers.PrimaryKeyRelatedField(
        queryset = UserProfile.objects.all(),
        #view_name='userprofile-detail',
        many=True,
        allow_null=True,
        default=[],
    )
    class Meta:
        model = Lab
        fields = ('url', 'id','name', 'created', 'info', 'photo',
                'cameras', 'projects', 'userprofiles')
