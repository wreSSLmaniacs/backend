from django.db import models
from django.db.models import fields
from rest_framework import serializers
from .models import Contest

class InfoSerializer(serializers.ModelSerializer):
    """Serializer for queries like contest rendering and past contest viewing that only need the problem statement"""
    class Meta:
        model = Contest
        fields = ('id','title','problem')


class ContestSerializer(serializers.ModelSerializer):
    """The default serializer"""
    class Meta:
        model = Contest
        fields = '__all__'

class DateInfoSerializer(serializers.ModelSerializer):
    """Serializer for views like dashboard which implement countdowns and event reloads and need time variables"""
    class Meta:
        model = Contest
        fields = ('id','title','problem','starttime','endtime')