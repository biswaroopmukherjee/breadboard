import time
from datetime import timedelta
import re

from django.shortcuts import render
from rest_framework import viewsets
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.generics import CreateAPIView
from rest_framework.exceptions import ParseError, NotFound
from rest_framework.response import Response
from django.core.signals import request_finished, request_started
from django.utils.decorators import method_decorator
from rest_framework.decorators import action
from django.views.decorators.cache import cache_page
from django.utils.dateparse import parse_datetime

from api.serializers import (
                ImageSerializerList,
                ImageSerializerDetail,
                ImageQuerySerializer,
                IMAGE_QUERY_MODES,
        )

from api.models import Image, Run, Lab

DEFAULT_DELTA = 7 # default delta value: range = center +- delta


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

    if query_mode=='Quick':
        # Quick mode: just get all images from a lab
        lab = Lab.objects.get(name=lab_name)
        queryset = lab.images.all()
        # TODO: paginate request
        context={'request': request}
        serializer = ImageSerializerList(queryset, many=True, context=context)
        return Response(serializer.data)

    elif query_mode=='DateTimeRange':
        # Names mode: get named images from a lab, and return with runtimes
        lab = Lab.objects.get(name=lab_name)
        queryset = lab.images.select_related('run').filter(created__range=datetimerange)
        # TODO: paginate request
        context={'request': request}
        serializer = ImageSerializerDetail(queryset, many=True, context=context)
        return Response(serializer.data)

    elif query_mode=='Names':
        # Names mode: get named images from a lab, and return with runtimes attached
        lab = Lab.objects.get(name=lab_name)
        queryset = lab.images.select_related('run').filter(name__in= namelist)
        if queryset.count()<len(namelist):
            raise NotFound(detail='Not all images were found')
        elif queryset.count()>len(namelist):
            raise NotFound(detail='Multiple images found with the same name. Try specifying created times.')
        # TODO: paginate request
        context={'request': request}
        serializer = ImageSerializerDetail(queryset, many=True, context=context)
        return Response(serializer.data)

    elif query_mode=='NamesCreated':
        # NamesCreated mode: Find images by name or if not found, associate run, and return with runtimes
        # Note: only this mode can create an image
        created_times = [parse_datetime(dt) for dt in createdlist]
        runtime_delta = timedelta(seconds=DEFAULT_DELTA)
        runtime_range_search = [(created_time-runtime_delta, created_time+runtime_delta) for created_time in created_times]

        lab = Lab.objects.get(name=lab_name)
        queryset = lab.images.select_related('run').filter(name__in= namelist)

        # First try to find by imagenames
        if not force_match and queryset.count()==len(namelist):
            context={'request': request}
            serializer = ImageSerializerDetail(queryset, many=True, context=context)
            return Response(serializer.data)
        else:
            # Otherwise, if forcing matching, or some images not found,
            #   create them, and match runtimes
            all_images = []
            # Note: handling param filtering on the client side

            for i in range(len(namelist)):
                try:
                    img = Image.objects.get(
                        name= namelist[i],
                        lab__name= lab_name,
                        created= createdlist[i]
                    )
                    if img.run == None or force_match:
                        print('No run attached or forcing matching: trying to find it')
                        try:
                            found_run = Run.objects.get(runtime__range=runtime_range_search[i])
                            img.run = found_run
                            print('Run attached to image')
                            img.save()
                        except Run.DoesNotExist:
                            raise NotFound(detail='warning: no run found')
                        except Run.MultipleObjectsReturned:
                            found_runs = Run.objects.filter(runtime__range=runtime_range_search[i])
                            img.run = found_runs[0]
                            print('Run attached to image')
                            img.save()
                            # raise NotFound(detail='warning: many runs found')

                except Image.DoesNotExist:
                    # if image not found, make a new image:
                    print('Creating new image object')
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
                    try:
                        found_run = Run.objects.get(runtime__range=runtime_range_search[i])
                        img.run = found_run
                        img.save()
                    except Run.DoesNotExist:
                        raise NotFound(detail='warning: no run found')
                    except Run.MultipleObjectsReturned:
                        raise NotFound(detail='warning: many runs found')

                except Image.MultipleObjectsReturned:
                    raise NotFound(detail='warning: many images found')

                all_images = all_images + [img]

            context={'request': request}
            serializer = ImageSerializerDetail(all_images, many=True, context=context)
            return Response(serializer.data)




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
    @method_decorator(cache_page(60*60*2))
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
    @method_decorator(cache_page(60*60*2))
    def create(self, request):
        '''
        Create methods
        '''
        if request.data=={}:
            # Default request
            return super().create(request)
        else:
            return handle_image_query(request, method='POST')
