from django.db import models
import os
from datetime import datetime

# Create your models here.

def inuplocate(instance,filename):
    """Function to generate URL for storage of input testcase"""
    return os.path.join("contests",str(instance.id),"in",filename)

def outuplocate(instance,filename):
    """Function to generate URL for storage of output testcase"""
    return os.path.join("contests",str(instance.id),"out",filename)

class Contest(models.Model):
    """Model to store everything related to a contest"""
    id = models.AutoField(primary_key=True)
    title   = models.CharField(max_length=64,blank=False,null=False)
    problem = models.TextField(blank=False,null=False)
    input = models.FileField(upload_to = inuplocate, blank=True,null=True) ##inputlocate used here
    output = models.FileField(upload_to = outuplocate, blank=True,null=True) ##outputlocate used here
    starttime = models.DateTimeField(default=datetime.now, blank=False,null=False)
    endtime = models.DateTimeField(default=datetime.now, blank=False,null=False)

class PointsTable(models.Model):
    """Stores one entry per user : Total Points"""
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=64,blank=False,null=False)
	points = models.IntegerField(blank=False,null=False)

class ContestUser(models.Model):
    """Stores one entry per (user,contest) pair : 
    Time of first successful submission and Points Obtained"""
	id = models.AutoField(primary_key=True)
	username = models.CharField(max_length=64,blank=False,null=False)
	compe = models.ForeignKey('Contest', models.DO_NOTHING)
	submittime = models.DateTimeField(default=datetime.now, blank=False)
	points = models.IntegerField(blank=False, null=False)