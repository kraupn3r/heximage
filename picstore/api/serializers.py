import datetime
import os
from rest_framework import serializers
from django.utils import timezone
from picstore.models import ImageSet, UploadedImage, TimedImageLink
from django.conf import settings



class UploadedImageSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        rep = super(UploadedImageSerializer, self).to_representation(instance)
        if instance.is_original:
            rep['size'] = ('{} x {}px').format(
                instance.file.width, instance.file.height)
        else:
            rep['size'] = str(instance.size) + 'px'
        request = self.context.get("request")
        rep['file'] = request.build_absolute_uri(instance.file.url)
        return rep

    class Meta:
        model = UploadedImage
        fields = [
            'id',
            'file',
            'size',
            'is_original',
        ]


class ListImageSetSerializer(serializers.ModelSerializer):
    files = UploadedImageSerializer(source='images', many=True, read_only=True)

    class Meta:
        model = ImageSet
        fields = [
            'files',
        ]


class UploadImageSetSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    file = serializers.ImageField()

    class Meta:
        model = ImageSet
        fields = [
            'file',
            'author'
        ]

    def validate_file(self, image):
        name, ext = os.path.splitext(image.name)
        if ext != '.jpg' and ext != '.png':
            raise serializers.ValidationError(
                "Only .jpg and .png file formats are allowed")
        if image.size > settings.MAX_FILE_SIZE:
            raise serializers.ValidationError("File size too big!")
        return image

    def create(self, validated_data):
        file_obj = validated_data.pop('file')
        instance = ImageSet.objects.create(**validated_data)
        name = instance.create_images(file_obj)
        instance.save()
        return instance


class RestrictedImageSerializer(serializers.ModelSerializer):

    image = serializers.CharField()
    delta = serializers.IntegerField(max_value=30000, min_value=300)

    class Meta:
        model = TimedImageLink
        fields = [
            'id',
            'image',
            'delta',
            'expire_by_date'
        ]
        read_only_fields = ['id', 'expire_by_date']

    def validate_image(self, value):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        try:
            image_obj = UploadedImage.objects.get(pk=value)
        except:
            raise serializers.ValidationError("Image of that id doesn't exist")

        if image_obj.set.author != user:
            raise serializers.ValidationError("Access Restricted")
        return value

    def create(self, validated_data):
        delta = validated_data.pop('delta')
        data = validated_data
        data['image'] = UploadedImage.objects.get(pk=data['image'])
        data['expire_by_date'] = timezone.now(
        ) + datetime.timedelta(seconds=delta)
        instance = TimedImageLink.objects.create(**validated_data)

        return instance
