import time
from datetime import timedelta

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
from django.utils.dateparse import parse_datetime

from api.serializers import (
                ImageSerializerList,
                ImageSerializerDetail
        )

from api.models import Image, Run, Lab

DEFAULT_DELTA = 7 # default delta value: range = center +- delta

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
        TODO: validate request
        (needs lab name, imagename, and created
        or lab name
        or labname and daterange)
        '''
        if request.query_params=={}:
            # Default request
            return super().list(request)
        else:
            # List all images from a lab
            if request.query_params.get('names') == None:
                lab = Lab.objects.get(name=self.request.query_params.get('lab'))
                queryset = lab.images.all()
                # TODO: paginate request
                context={'request': request}
                serializer = ImageSerializerList(queryset, many=True, context=context)
                return Response(serializer.data)

            # Otherwise return images requested
            else:

                # TODO: separate names into array imagenames[]
                imagenames = [request.query_params.get('names', None)]
                created_time = parse_datetime(self.request.query_params.get('created'))
                runtime_delta = timedelta(seconds=DEFAULT_DELTA)
                runtime_range_search = (created_time-runtime_delta, created_time+runtime_delta)

                all_images = []
                # Note: handling param filtering on the client side

                # Single image, all params
                for i in range(len(imagenames)):

                    filter_clean = {
                        'name' : imagenames[i],
                        'lab__name' : self.request.query_params.get('lab', None),
                        'created' : self.request.query_params.get('created', None)
                    }
                    try:
                        img = Image.objects.get(**filter_clean)
                        if img.run == None:
                            print('No run attached: trying to find it')
                            try:
                                found_run = Run.objects.get(runtime__range=runtime_range_search)
                                img.run = found_run
                                print('Run attached to image')
                                img.save()
                            except Run.DoesNotExist:
                                # TODO: handle this better
                                print('warning: no run found')
                            except Run.MultipleObjectsReturned:
                                # TODO: handle this better
                                print('warning: many runs found')

                    except Image.DoesNotExist:
                        # if image not found, make a new image:
                        print('Creating new image object')
                        lab = Lab.objects.get(name=filter_clean.get('lab__name'))

                        img = lab.images.create(
                            name = filter_clean.get('name'),
                            created = filter_clean.get('created'),
                            )
                        try:
                            found_run = Run.objects.get(runtime__range=runtime_range_search)
                            img.run = found_run
                            img.save()
                        except Run.DoesNotExist:
                            # TODO: handle this better
                            print('warning: no run found')
                        except Run.MultipleObjectsReturned:
                            # TODO: handle this better
                            print('warning: many runs found')

                    except Image.MultipleObjectsReturned:
                        #todo: handle better
                        print('warning: many images found with the same name')

                    all_images = all_images + [img]

                context={'request': request}
                serializer = ImageSerializerDetail(all_images, many=True, context=context)
                return Response(serializer.data)
