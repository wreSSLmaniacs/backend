from users.models import Users, AuthUser
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    """Default serializer for auth usr"""
    class Meta:
        model = AuthUser
        fields = '__all__'
        
class profileSerializer(serializers.ModelSerializer):
    """Serializer to get he profile of the user"""
    userSl = UserSerializer(read_only=True)
    class Meta:
        model = Users
        fields = '__all__'

class profileDetailSerializer(serializers.ModelSerializer):
    """Serializer to get all the details of the users"""
    userSl = UserSerializer(read_only=True)
    class Meta:
        model = Users
        fields = '__all__'
        depth = 1
