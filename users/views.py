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
    filename = request.data.get("filename")
    language = request.data.get("language")
    inp = request.data.get("input")

    if os.path.exists('codes/'+filename):
        f = open('./codes/in.txt','w')
        f.write(inp)
        f.close()

        if language == 'cpp':
            cmd = ' g++ codes/{0} -o codes/a.out'.format(filename)
            os.system(cmd)
            os.system('./codes/a.out < ./codes/in.txt > ./codes/out.txt')
        if language == 'python':
            cmd = ' python3 codes/{0} < ./codes/in.txt > ./codes/out.txt'.format(filename)
            os.system(cmd)

        f = open('./codes/out.txt','r')
        output = f.read()
        f.close()
        data = {
            "output": output
        }
        os.system('rm -f codes/*.txt codes/a.out ')
        return JsonResponse(data, status=HTTP_200_OK)
    return JsonResponse({'error': ['File does not exist']})

@api_view(['POST'])
def display(request):
    filename = request.data.get("filename")
    f = open('./codes/{0}'.format(filename),'r')
    script = f.read()
    data = {
        "script": script
    }
    return JsonResponse(data, status=HTTP_200_OK)

class image(APIView):
    parser_class = [FileUploadParser, DjangoMultiPartParser, MultiPartParser]
    
    def post(self, request, format=None):
        if request.method == 'POST' and request.FILES['code']:
            try:
                myfile = request.FILES['code']
                fs = FileSystemStorage(location='media/codes/')
                filename = fs.save(myfile.name, myfile)
                url = ('http://127.0.0.1:8000'+'/media/codes/'+str(filename))
            except:
                return JsonResponse({'error': ['Invalid file reqeust']}, status=HTTP_400_BAD_REQUEST)
                
            data = {
                "url": url
            }
            return JsonResponse(data, status=HTTP_200_OK)
        return JsonResponse({'error': ['Invalid Request']})
    

