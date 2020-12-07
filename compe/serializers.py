from django.db import models
from rest_framework import serializers
from .models import Contest

class InfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contest
        fields = ('id','title','problem')


class ContestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contest
        fields = '__all__'