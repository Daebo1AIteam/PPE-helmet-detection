from django.db import models

# Create your models here.

class Member(models.Model):
    memberno = models.AutoField(db_column='memberNo', primary_key=True)
    email = models.CharField(db_column='email',max_length = 255)
    class Meta:
        managed = False
        db_table = 'member'