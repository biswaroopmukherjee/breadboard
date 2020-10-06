import time
from datetime import timedelta
import re

from django.shortcuts import render
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from django.core.signals import request_finished, request_started
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.utils.dateparse import parse_datetime

from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.generics import CreateAPIView
from rest_framework.exceptions import ParseError, NotFound
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.decorators import action


from api.serializers import (
                ImageSerializerList,
                ImageSerializerDetail,
                ImageQuerySerializer,
                IMAGE_QUERY_MODES,
        )

from api.models import Image, Run, Lab

from breadboard.secrets import secrets as secrets

import pusher

pusher_client = pusher.Pusher(
  app_id=secrets.PUSHER_APP_ID,
  key=secrets.PUSHER_KEY,
  secret=secrets.PUSHER_SECRET,
  cluster='us2',
  ssl=True
)

DEFAULT_DELTA = 7 # default delta value: range = center +- delta


# The style to use for queryset pagination.
pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
paginator = pagination_class()



def serialize_and_paginate_queryset(queryset, request, mode='detail'):
    # Paginate request and then serialize it 
    page = paginator.paginate_queryset(queryset, request)
    context={'request': request}

    if mode=='list':        serializer_function = ImageSerializerList
    elif mode=='detail':    serializer_function = ImageSerializerDetail

    if page is not None:
        serializer = serializer_function(page, many=True, context=context)
        return paginator.get_paginated_response(serializer.data)
    serializer = serializer_function(queryset, many=True, context=context)
    return Response(serializer.data)


def handle_image_query(request, method):

    # Parse query
    if method=='GET':
        requestdata = request.query_params
    else:
        requestdata = request.data
    imagequery = ImageQuerySerializer(data=requestdata)
    imagequery.is_valid(raise_exception=True)

    query_mode = imagequery.validated_data.get('query_mode')
    lab_name = imagequery.validated_data.get('lab')
    namelist = imagequery.validated_data.get('namelist')
    createdlist = imagequery.validated_data.get('createdlist')
    datetimerange = (
                imagequery.validated_data.get('start_datetime'),
                imagequery.validated_data.get('end_datetime'),
            )
    force_match = imagequery.validated_data.get('force_match')

    lab = Lab.objects.get(name=lab_name)

    if query_mode=='Quick':
        # Quick mode: just get all images from a lab
        queryset = lab.images.all()
        return serialize_and_paginate_queryset(queryset, request, mode='list')

    elif query_mode=='DateTimeRange':
        # Names mode: get named images from a lab, and return with runtimes
        lab = Lab.objects.get(name=lab_name)
        queryset = lab.images.select_related('run').filter(created__range=datetimerange)
        return serialize_and_paginate_queryset(queryset, request, mode='detail')

    elif query_mode=='Names':
        # Names mode: get named images from a lab, and return with runtimes attached
        lab = Lab.objects.get(name=lab_name)
        queryset = lab.images.select_related('run').filter(name__in= namelist)
        if queryset.count()<len(namelist):
            raise NotFound(detail='Not all images were found')
        elif queryset.count()>len(namelist):
            raise NotFound(detail='Multiple images found with the same name. Try specifying created times.')
        return serialize_and_paginate_queryset(queryset, request, mode='detail')

    elif query_mode=='NamesCreated':
        # NamesCreated mode: Find images by name or if not found, associate run, and return with runtimes
        # Note: only this mode can create an image
        created_times = [parse_datetime(dt) for dt in createdlist]
        runtime_delta = timedelta(seconds=DEFAULT_DELTA)
        runtime_range_search = [(created_time-runtime_delta, created_time+runtime_delta) for created_time in created_times]

        lab = Lab.objects.get(name=lab_name)
        queryset = lab.images.select_related('run').filter(name__in=namelist)

        # First try to find by imagenames
        if not force_match and queryset.count()==len(namelist):
            print('Images found. Not force matching')
            return serialize_and_paginate_queryset(queryset, request, mode='detail')

        else:
            # Otherwise, if forcing matching, or some images not found,
            #   create them, and match runtimes
            all_images = []
            # Note: handling param filtering on the client side

            for i in range(len(namelist)):
                # I used to have a try/except here, now I use count() to check the queryset
                matched_images = Image.objects.filter(
                    name= namelist[i],
                    lab__name= lab_name,
                    created= createdlist[i]
                )
                print(matched_images.count())
                numimages = matched_images.count()
                if numimages>1:
                    print('Warning: multiple images found for imagename = ' + namelist[i])
                    # Remove copies
                    for img in matched_images[1:]:
                        img.delete()
                elif numimages==0:
                    # if image not found, make a new image:
                    # TODO: use serializer for this part
                    print('Creating new image object')
                    pusher_client.trigger(lab_name, 'new-image', {'message': 'new image'})
                    img = lab.images.create(
                        name = namelist[i],
                        created = createdlist[i],
                        notes = imagequery.validated_data.get('notes'),
                        filepath = imagequery.validated_data.get('filepath'),
                        tags = imagequery.validated_data.get('tags'),
                        thumbnail = imagequery.validated_data.get('thumbnail'),
                        total_atoms = imagequery.validated_data.get('total_atoms'),
                        odpath = imagequery.validated_data.get('odpath'),
                        atomsperpixel = imagequery.validated_data.get('atomsperpixel'),
                        cropi = imagequery.validated_data.get('cropi'),
                        settings = imagequery.validated_data.get('settings'),
                        pixel_size = imagequery.validated_data.get('pixel_size'),
                        atom = imagequery.validated_data.get('atom'),
                        bad_shot = imagequery.validated_data.get('bad_shot')
                        )
                    
                # always pick the first result for multiple images
                img = matched_images[0]


                # attach a run to the image                    
                try:
                    found_run = Run.objects.get(runtime__range=runtime_range_search[i], lab__name= lab_name)
                    img.run = found_run
                    print('Run attached to image')
                    img.save()
                except Run.DoesNotExist:
                    print('Warning: no run found')
                    # raise NotFound(detail='warning: no run found')
                except Run.MultipleObjectsReturned:
                    found_runs = Run.objects.filter(runtime__range=runtime_range_search[i], lab__name= lab_name)
                    img.run = found_runs[0]
                    print('Run attached to image')
                    img.save()
                    # raise NotFound(detail='warning: many runs found')

                all_images = all_images + [img]


            return serialize_and_paginate_queryset(all_images, request, mode='detail')



class ImageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows images to be viewed or edited
    """
    def get_serializer_class(self):
        if self.action == 'list':
            return ImageSerializerList
        if self.action == 'retrieve':
            return ImageSerializerDetail
        return ImageSerializerDetail


    queryset = Image.objects.all()

    # Cache page for the requested url
    # @method_decorator(cache_page(60*60*2))
    def list(self, request):
        '''
        List methods
        '''
        if request.query_params=={}:
            # Default request
            return super().list(request)
        else:
            return handle_image_query(request, method='GET')


    # Cache page for the requested url
    # @method_decorator(cache_page(60*60*2))
    def create(self, request):
        '''
        Create methods
        '''
        if request.data=={}:
            # Default request
            return super().create(request)
        else:
            return handle_image_query(request, method='POST')
