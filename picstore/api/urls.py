from django.contrib import admin
from django.urls import path
from .views import ImageSetAPIView, CreateLinkAPIView, RestrictedTimeView
app_name = 'picstore'

urlpatterns = [
    path('', ImageSetAPIView.as_view()),
    path('create/', CreateLinkAPIView.as_view()),
    path('<uuid:uuid>/', RestrictedTimeView, name='timelink')
]
