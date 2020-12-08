from projects.models import UserFiles
from rest_framework import serializers

class userFilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFiles
        fields = '__all__'