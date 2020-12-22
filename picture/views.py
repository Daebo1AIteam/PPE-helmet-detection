from rest_framework import status, viewsets
from webcam.models import Picture
from webcam.serializers import PictureSerializer
class PictureViewSet(viewsets.ModelViewSet):
	serializer_class = PictureSerializer
	queryset = Picture.objects.all()

"""
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from rest_framework import generics
from rest_framework import mixins

from .models import Lecture
from .serializers import LectureSerializer
# Create your views here.
"""