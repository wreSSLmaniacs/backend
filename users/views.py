from users.models import Users
from django.http.response import JsonResponse
from rest_framework.status import *
from rest_framework.views import APIView
from django.shortcuts import render
from rest_framework import exceptions
from django.contrib.auth import authenticate
from django.http import HttpResponse
from rest_framework.decorators import api_view
from users.models import *
from django.contrib.auth.models import User, Group
from django.core.files.storage import FileSystemStorage
from rest_framework.parsers import JSONParser, FileUploadParser, MultiPartParser, DjangoMultiPartParser, FormParser
from users.serializers import *
import os

# Create your views here.
@api_view(['GET', 'PUT'])
def userList(request):
    if request.method == 'GET':
        obj = Users.objects.all()
        title = request.GET.get('title', None)
        if title is not None:
           obj  = obj.filter(title__icontains=title)
        serializer = profileDetailSerializer(obj, many=True)
        return JsonResponse(serializer.data, safe=False)
    
@api_view(['GET', 'PUT'])
def userDetail(request, pk):
    if request.method == 'GET':
        try:
            obj = Users.objects.get(pk=pk)
        except:
            return JsonResponse("error", status=HTTP_404_NOT_FOUND)
        
        serializer = profileDetailSerializer(obj)
        return JsonResponse(serializer.data)
    
@api_view(['POST'])
def registerUser(request):
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        image = request.data.get('image')
        
        try:
            User.objects.get(username=username)
        except:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
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

@api_view(['POST'])
def login_user(request):
    username = request.data.get("username")
    password = request.data.get("password")
    user = authenticate(username=username, password=password)
    if user is not None:
        return JsonResponse({'token':'Logged in succesfully'}, status=HTTP_200_OK)
    return JsonResponse({'error': ['Invalid User']}, status=HTTP_404_NOT_FOUND)

@api_view(['POST'])
def compile(request):
    # filename = request.data.get("filename")
    script = request.data.get("script")
    language = request.data.get("language")
    # user = request.data.get("username")
    inp = request.data.get("input")

    # if os.path.exists('codes/{0}'.format(filename)):
    f = open('./codes/in.txt','w')
    f.write(inp)
    f.close()

    if language == 'c_cpp':
        g = open('./codes/temp.cpp','w')
        g.write(script)
        g.close()
        cmd = ' g++ codes/temp.cpp -o codes/a.out'
        val = os.system(cmd)
        if val == 256:
            return JsonResponse({'success': False, 'output': ['Compilation Error']})
        val = os.system('./codes/a.out < ./codes/in.txt > ./codes/out.txt')
        if val == 6:
            return JsonResponse({'success': False, 'output': ['Runtime Error']})

    if language == 'python':
        g = open('./codes/temp.py','w')
        g.write(script)
        g.close()
        cmd = ' python3 codes/temp.py < ./codes/in.txt > ./codes/out.txt'
        val = os.system(cmd)
        if val == 256:
            return JsonResponse({'success': False, 'output': ['Compilation Error']})

    f = open('./codes/out.txt','r')
    output = f.read()
    f.close()
    data = {
        "success": True,
        "output": output
    }
    os.system('rm -f codes/*.txt codes/a.out ')
    return JsonResponse(data, status=HTTP_200_OK)
    # return JsonResponse({'error': ['File does not exist']}, status=HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def display(request):
    filename = request.data.get("filename")
    # user = request.data.get("username")
    f = open('./codes/{0}'.format(str(filename)),'r')
    script = f.read()
    data = { "script": script }
    return JsonResponse(data, status=HTTP_200_OK)

@api_view(['GET','POST'])
def file(request):
    if request.method == 'POST':
        script = request.data.get("script")
        filename = request.data.get("filename")
        # user = request.data.get("username")
        try:
            if script is not None:
                if not os.path.isdir('./codes'):
                    os.mkdir('./codes')
                # if not os.path.isdir('./codes/{0}'.format(str(user))):
                #     path = './codes/{0}'.format(str(user))
                #     os.mkdir(path)
                f = open('./codes/{0}'.format(str(filename)), 'w')
                f.write(script)
                f.close()
                # url = ('http://127.0.0.1:8000'+'/codes/'+str(filename))
        except:
            return JsonResponse({'error': ['Invalid file reqeust']}, status=HTTP_400_BAD_REQUEST)
        data = {"filename":filename, "script": script }
        return JsonResponse(data, status=HTTP_200_OK)
    # else:  
    #     data = []
    #     for filename in os.listdir('./codes'):
    #         f = open('./codes/{0}'.format(filename), 'r')
    #         script = f.read()
    #         data.append({"filename": filename, "script": script})
    #     return JsonResponse(data, status=HTTP_200_OK)
    

