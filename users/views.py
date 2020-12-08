from django.http.response import JsonResponse
from rest_framework.status import *
from rest_framework.views import APIView
from django.shortcuts import render
from rest_framework import exceptions
from django.contrib.auth import authenticate
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from users.models import *
from django.contrib.auth.models import User, Group
from django.core.files.storage import FileSystemStorage
from rest_framework.parsers import JSONParser, FileUploadParser, MultiPartParser, DjangoMultiPartParser, FormParser
from users.serializers import *
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

import os

# Create your views here.
@api_view(['GET', 'PUT'])
@authentication_classes([TokenAuthentication])
def userList(request):
    if request.method == 'GET':
        obj = Users.objects.all()
        title = request.GET.get('title', None)
        if title is not None:
           obj  = obj.filter(title__icontains=title)
        serializer = profileDetailSerializer(obj, many=True)
        return JsonResponse(serializer.data, safe=False)
    
@api_view(['GET', 'PUT'])
@authentication_classes([TokenAuthentication])
def userDetail(request, pk):
    if request.method == 'GET':
        try:
            obj = Users.objects.get(pk=pk)
        except:
            return JsonResponse("error", status=HTTP_404_NOT_FOUND, safe=False)
        
        serializer = profileDetailSerializer(obj)
        return JsonResponse(serializer.data, safe=False)

@api_view(['POST'])
def userpk(request):
    if request.method == 'POST':
        uname = request.data.get('username')
        try:
            obj = User.objects.get(username=uname)
            obj = Users.objects.get(user_fk=obj.pk)
        except:
            return JsonResponse("error invalid user", status=HTTP_404_NOT_FOUND, safe=False)
        
        serializer = profileDetailSerializer(obj)
        return JsonResponse(serializer.data, safe=False)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
def registerUser(request):
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        image = request.data.get('image')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        
        try:
            User.objects.get(username=username)
        except:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            user.set_password(password)
            user.save()
            
            userId = User.objects.get(username=username).pk
            
            serializer = profileSerializer(data={
                'user_fk': userId,
                'image': image
            })
            
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data, status=HTTP_201_CREATED) 
            
            User.objects.get(username=username).delete()
            return JsonResponse(serializer.errors, status=HTTP_400_BAD_REQUEST, safe=False)
    
        return JsonResponse({"error":["This username already taken"]}, status=HTTP_404_NOT_FOUND, safe=False)

# @permission_classes([IsAuthenticated])
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
def login_user(request):
    username = request.data.get("username")
    password = request.data.get("password")
    user = authenticate(username=username, password=password)
    user2 = Users.objects.get(user_fk=user.pk)
    if user is not None:
        data = {
            'token':'Logged in succesfully',
            'username':username,
            'image':user2.image,
            'userid':user2.pk
        }
        return JsonResponse(data, status=HTTP_200_OK)
    return JsonResponse({'error': ['Invalid User']}, status=HTTP_404_NOT_FOUND)

class image(APIView):
    parser_class = [FileUploadParser, DjangoMultiPartParser, MultiPartParser]
    
    def post(self, request, format=None):
        if request.method == 'POST' and request.FILES['image']:
            try:
                myfile = request.FILES['image']
                fs = FileSystemStorage(location='media/')
                myfile.name = "profile.png"
                filename = fs.save(myfile.name, myfile)
                url = ('http://127.0.0.1:8000'+'/media/'+str(filename))
            except:
                return JsonResponse({'error': ['Invalid file reqeust']}, status=HTTP_400_BAD_REQUEST)
                
            data = {
                "url": url
            }
            return JsonResponse(data, status=HTTP_200_OK)
        return JsonResponse({'error': ['Invalid Request']})