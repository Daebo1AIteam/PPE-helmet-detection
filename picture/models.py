from django.db import models


class Picture(models.Model):
    picture_name = models.TextField(primary_key='True')


class Statstics(models.Model):
    created_date = models.TextField(primary_key='True')
    count = models.IntegerField(default=0)

