from django.shortcuts import render
from django.shortcuts import redirect
import urllib

# Create your views here.
def LoginView(request):
    return render(request, "login.html")

def SuccessView(request):
    return render(request, "success.html")





# from rest_framework import status, viewsets
# from webcam.models import Picture
# from webcam.serializers import PictureSerializer
# 
# class PictureViewSet(viewsets.ModelViewSet):
# 	serializer_class = PictureSerializer
# 	queryset = Picture.objects.all()
# 