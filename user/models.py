from django.db import models
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser)

# Create your models here.

class Member(models.Model):
    email = models.CharField(max_length = 255)