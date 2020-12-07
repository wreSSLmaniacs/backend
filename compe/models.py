from django.db import models
import os

# Create your models here.

def inuplocate(instance,filename):
    return os.path.join("contests",str(instance.id),"in",filename)

def outuplocate(instance,filename):
    return os.path.join("contests",str(instance.id),"out",filename)

class Contest(models.Model):
    id = models.AutoField(primary_key=True)
    title   = models.CharField(max_length=64,blank=False,null=False)
    problem = models.TextField(blank=False,null=False)
    input = models.FileField(upload_to = inuplocate, blank=True,null=True)
    output = models.FileField(upload_to = outuplocate, blank=True,null=True)