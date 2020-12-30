from rest_framework import serializers
from .models import Picture,Statstics


class PictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Picture
        fields = '__all__'

class StatsticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Statstics
        fields = '__all__'