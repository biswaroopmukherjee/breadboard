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
                RunSerializerList,
                RunSerializerDetail,
        )

from api.models import Run


class RunViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows runs to be viewed or edited
    """
    def get_serializer_class(self):
        if self.action == 'list':
            return RunSerializerList
        if self.action == 'retrieve':
            return RunSerializerDetail
        return RunSerializerDetail

    # Cache page for the requested url
    @method_decorator(cache_page(60*60*2))
    def list(self, request):
        return super().list(request)

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
