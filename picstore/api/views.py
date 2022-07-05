import json

from django.urls import reverse
from django.http import HttpResponse, HttpResponseForbidden, StreamingHttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, permissions, status
from rest_framework.settings import api_settings
from rest_framework.parsers import MultiPartParser
from picstore.models import ImageSet, UploadedImage, TimedImageLink
from picstore.api.serializers import UploadedImageSerializer, \
    ListImageSetSerializer, UploadImageSetSerializer, RestrictedImageSerializer
from accounts.models import UserProfile
from django.utils import timezone
from wsgiref.util import FileWrapper
from io import StringIO
import requests
from PIL import Image

class ImageSetAPIView(generics.GenericAPIView):
    parser_classes = (MultiPartParser, )
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UploadImageSetSerializer
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS

    def get_queryset(self):
        queryset = ImageSet.objects.filter(author=self.request.user)
        return queryset

    def get(self, request, format=None):
        qs = self.get_queryset()
        page = self.paginate_queryset(qs)

        if page is not None:
            serializer = ListImageSetSerializer(page, many=True,
                context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = ListImageSetSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = UploadImageSetSerializer(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({'detail': 'Thumbnails have been created!'},
                            status=status.HTTP_200_OK)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


class CreateLinkAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RestrictedImageSerializer

    def post(self, request, format=None):
        serializer = RestrictedImageSerializer(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            instance = serializer.save()
            response_data = {}
            response_data['detail'] = 'Succesfully created!'
            response_data['expiry date'] = instance.expire_by_date.strftime(
                '%Y/%m/%d - %H:%M:%S')
            response_data['URI'] = request.build_absolute_uri(
                reverse('picstore:timelink', kwargs={'uuid': instance.id}))
            return Response(response_data,
                            status=status.HTTP_200_OK)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)



def url2yield(url, chunksize=1024):
   s = requests.Session()
   response = s.get(url, stream=True)

   chunk = True
   while chunk :
      chunk = response.raw.read(chunksize)

      if not chunk:
         break

      yield chunk



def RestrictedTimeView(request, uuid):

    link_obj = TimedImageLink.objects.get(id=uuid)
    if link_obj.expire_by_date > timezone.now():
        filepath = link_obj.image.file.url
        response = StreamingHttpResponse(url2yield(filepath), content_type="image/jpeg")

    else:
        response = HttpResponseForbidden(
            "403 Forbidden , you don't have access")
    return response
