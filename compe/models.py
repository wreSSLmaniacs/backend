from django.db import models

# Create your models here.

class Contest(models.Model):
    id = models.AutoField(primary_key=True)
    title   = models.CharField(max_length=64,blank=False,null=False,default="My Contest")
    problem = models.TextField(blank=False,null=False,default="My Problem Statement")

class TestCases(models.Model):
    id = models.AutoField(primary_key=True)
    contest = models.ForeignKey(Contest,models.DO_NOTHING,db_column="contest")
    index = models.IntegerField()
    input = models.FileField(upload_to="testcases/inputs/{0}/{1}/".format(contest,index))
    output = models.FileField(upload_to="testcases/outputs/{0}/{1}/".format(contest,index))