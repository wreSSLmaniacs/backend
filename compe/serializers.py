from rest_framework import serializers
from .models import Contest, TestCases

class ContestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contest
        fields = '__all__'

class TestCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCases
        fields = '__all__'