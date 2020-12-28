from django.db import models

class Picture(models.Model):
    picture_name = models.TextField(primary_key='True')

