import json
from django.urls import reverse
from django.http import HttpResponse, HttpResponseForbidden
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

# Seems like the only way to restrict access to a file in pure django,
# could also create new file withing the view, load it, then delete and serve
def RestrictedTimeView(request, uuid):
    # open file
    link_obj = TimedImageLink.objects.get(id=uuid)
    filepath = link_obj.image.file.path

# image is loaded to memory and then passed to end user, not showing the source
    with open(filepath, "rb") as fid:
        filedata = fid.read()

    if link_obj.expire_by_date > timezone.now():
        response = HttpResponse(filedata, content_type="image/jpeg")
    else:
        response = HttpResponseForbidden(
            "403 Forbidden , you don't have access")
    return response
