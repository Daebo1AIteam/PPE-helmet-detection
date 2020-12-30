from rest_framework import status, viewsets
from .models import Picture,Statstics
from .serializers import PictureSerializer,StatsticsSerializer

class PictureViewSet(viewsets.ModelViewSet):
	serializer_class = PictureSerializer
	queryset = Picture.objects.all()

class StatsticsViewSet(viewsets.ModelViewSet):
	serializer_class = StatsticsSerializer
	queryset = Statstics.objects.all()
