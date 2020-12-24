from django.db import models

class Picture(models.Model):
    picture_name = models.TextField()
#    picture_image=models.ImageField(upload_to='picture',null = True)


