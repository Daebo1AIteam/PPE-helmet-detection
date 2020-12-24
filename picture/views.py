from rest_framework import status, viewsets
from webcam.models import Picture
from webcam.serializers import PictureSerializer

class PictureViewSet(viewsets.ModelViewSet):
	serializer_class = PictureSerializer
	queryset = Picture.objects.all()

