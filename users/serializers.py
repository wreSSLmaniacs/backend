from users.models import Users, UserFiles
from users.models import AuthUser
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthUser
        fields = '__all__'
        
class profileSerializer(serializers.ModelSerializer):
    userSl = UserSerializer(read_only=True)
    class Meta:
        model = Users
        fields = '__all__'

class profileDetailSerializer(serializers.ModelSerializer):
    userSl = UserSerializer(read_only=True)
    class Meta:
        model = Users
        fields = '__all__'
        depth = 1

class userFilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFiles
        fields = '__all__'
