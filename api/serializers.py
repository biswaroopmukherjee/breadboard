import re

from django.contrib.auth.models import User, Group
from rest_framework import serializers
from api.models import (
        Image, Run, Dataset,
        Project, Lab, UserProfile
        )

IMAGE_QUERY_MODES = [
    'Quick',
    'Names',
    'NamesCreated',
    'DateTimeRange',
]

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
                'projects', 'userprofiles')




class RunSerializerList(serializers.ModelSerializer):
    class Meta:
        model = Run
        fields = ('url', 'id','created', 'runtime', 'parameters', 'bad_shot',
                    'notes', 'workday', 'dataset')

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
                    'atomsperpixel', 'thumbnail', 'run', 'pixel_size')

class ImageSerializerDetail(serializers.ModelSerializer):
    run = RunSerializerList(many=False, read_only=True)
    class Meta:
        model = Image
        fields = ('url', 'id','name', 'created', 'notes', 'filepath', 'tags',
                    'cropi', 'atom', 'odpath', 'total_atoms', 'settings',
                    'atomsperpixel', 'thumbnail', 'run', 'pixel_size')



class ImageQuerySerializer(serializers.Serializer):
    # Allows us to validate get queries sent to imageviews
    lab = serializers.CharField(required=True)
    names = serializers.CharField(required=False)
    namelist = serializers.ListField(child=serializers.CharField(), required=False)
    created = serializers.CharField(required=False)
    createdlist = serializers.ListField(child=serializers.DateTimeField(), required=False)
    start_datetime = serializers.DateTimeField(required=False)
    end_datetime = serializers.DateTimeField(required=False)
    query_mode = serializers.ChoiceField(choices=IMAGE_QUERY_MODES, default='Quick')
    force_match = serializers.BooleanField(default=False)

    # parameters for posting image information
    postparams = ['notes', 'filepath', 'tags',
                'cropi', 'atom', 'odpath', 'total_atoms', 'settings',
                'atomsperpixel', 'thumbnail', 'pixel_size']
    notes = serializers.CharField(required=False)
    filepath = serializers.CharField(required=False)
    tags = serializers.JSONField(required=False)
    thumbnail = serializers.CharField(required=False)
    total_atoms = serializers.CharField(required=False)
    odpath = serializers.CharField(required=False)
    atomsperpixel = serializers.CharField(required=False)
    cropi = serializers.JSONField(required=False)
    settings = serializers.JSONField(required=False)
    pixel_size = serializers.FloatField(required=False)
    atom = serializers.CharField(required=False)

    def validate(self, data):
        DateTimeRange = False
        NamesCreated = False
        # create equal length arrays for image names and datetimes
        if data.get('names')!=None and data.get('created')!=None:
            NamesCreated = True
            data['query_mode'] = 'NamesCreated'
            namelist = re.split(',', data['names'])
            createdlist = re.split(',', data['created'])
            if len(namelist) == len(createdlist):
                data['namelist'] = namelist
                data['createdlist'] = createdlist
            else:
                raise serializers.ValidationError("need equal lengths of imagenames and created datetimes")

        # create array for imagenames only
        elif (data.get('names')!=None) and (data.get('created')==None):
            NamesCreated = True
            data['query_mode'] = 'Names'
            data['namelist'] = re.split(',', data['names'])

        elif (data.get('names')==None) and (data.get('created')!=None):
            raise serializers.ValidationError("need imagenames")

        # validate start and end datetime requests (if either are provided)
        if data.get('start_datetime')!=None or data.get('end_datetime')!=None:
            # if only onle is provided
            if data.get('start_datetime')==None or data.get('end_datetime')==None:
                raise serializers.ValidationError("need both end and start")
            # if start is after end
            elif data.get('start_datetime') > data.get('end_datetime'):
                raise serializers.ValidationError("end must occur after start")
            else:
                DateTimeRange = True
                data['query_mode'] = 'DateTimeRange'

        # # Post parameters
        # l = [out.get(param) for param in postparams] # find if any of the params have been supplied
        # if not l.count(None) == len(l) and (',' in  data['names']):
        #     # if we sent a param with multiple images
        #     print('Warning: applying a single param to multiple images')

        # Validation errors
        if DateTimeRange and NamesCreated:
            raise serializers.ValidationError("Use either a list of names or a datetime range to find images")

        if data.get('force_match') and (data.get('created')==None):
            raise serializers.ValidationError("Please provide image created times to match with runtimes")


        return data
