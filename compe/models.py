from django.db import models
import os
from datetime import datetime

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
    starttime = models.DateTimeField(default=datetime.now, blank=True)
    endtime = models.DateTimeField(default=datetime.now, blank=True)

class PointsTable(models.Model):
	id = models.AutoField(primary_key=True)
	username = models.CharField(max_length=64,blank=False,null=False)
	points = models.IntegerField(blank=False,null=False)

class ContestUser(models.Model):
	id = models.AutoField(primary_key=True)
	username = models.CharField(max_length=64,blank=False,null=False)
	compe = models.ForeignKey('Contest', models.DO_NOTHING)
	submittime = models.DateTimeField(default=datetime.now, blank=True)
	points = models.IntegerField(blank=False, null=False)
