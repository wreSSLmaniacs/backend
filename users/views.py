from users.models import Users, UserFiles
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

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
def compile(request):
    # filename = request.data.get("filename")
    script = request.data.get("script")
    language = request.data.get("language")
    inp = request.data.get("input")
    user = request.data.get("username")  # Check this

    if not os.path.exists('codes/{}'.format(user)):
        os.system('mkdir ./codes/{}'.format(user))
        
    os.system('touch ./codes/{}/in.txt'.format(user))
    os.system('touch ./codes/{}/out.txt'.format(user))
    os.system('touch ./codes/{}/code_temp.cpp'.format(user))
    os.system('touch ./codes/{}/code_temp.py'.format(user))
    os.system('touch ./codes/{}/code_temp.rb'.format(user))
    os.system('touch ./codes/{}/script.sh'.format(user))
    
    f = open('./codes/{}/in.txt'.format(user),'w')
    f.write(inp)
    f.close()

    if language == 'c_cpp':
        g = open('./codes/{}/code_temp.cpp'.format(user),'w')
        g.write(script)
        g.close()

        os.system('docker run --name cppbox -v "$(pwd)"/codes/{}/:/code --rm -t -d cppenv'.format(user))    # This will start a container
        val = os.system('docker exec cppbox /bin/sh -c "g++ code_temp.cpp > log 2>&1; ./a.out < in.txt > out.txt 2>&1"')       # This will execute our commands (inside container)
        
        os.system('docker stop cppbox')
        f = open("./codes/{}/log".format(user), "r")
        f2 = open("./codes/{}/out.txt".format(user), "r")
        log = f.read()
        log += f2.read()
        f.close()
        f2.close()
        
        # if val == 256:
        if val == 32512:
            return JsonResponse({'success': False, 'output': ['Compilation Error:\n {}'.format(log)]})
        if val == 34816:
            return JsonResponse({'success': False, 'output': ['Runtime Error: \n'.format(log)]})
        if val != 0:
            return JsonResponse({'success': False, 'output': ['Unexpected Error: \n'.format(log)]})

    elif language == 'python':
        g = open('./codes/{}/code_temp.py'.format(user),'w')
        g.write(script)
        g.close()
        
        os.system('docker run --name pybox -v "$(pwd)"/codes/{}/:/code --rm -t -d pyenv'.format(user))    # This will start a container
        val = os.system('docker exec pybox /bin/sh -c "python3 code_temp.py < in.txt > out.txt 2>&1"')       # This will execute our commands (inside container)
        
        os.system('docker stop pybox')
        f = open("./codes/{}/out.txt".format(user), "r")
        log = f.read();
        f.close();
        
        if val == 256:
            return JsonResponse({'success': False, 'output': ['Compilation Error:\n {}'.format(log)]})

    elif language == 'r':
        g = open('./codes/{}/code_temp.rb'.format(user),'w')
        g.write(script)
        g.close()
        
        os.system('docker run --name rubybox -v "$(pwd)"/codes/{}/:/code --rm -t -d rubyenv'.format(user))    # This will start a container
        val = os.system('docker exec rubybox /bin/sh -c "ruby code_temp.rb < in.txt > out.txt 2>&1"')       # This will execute our commands (inside container)
        
        os.system('docker stop rubybox')
        f = open("./codes/{}/out.txt".format(user), "r")
        log = f.read();
        f.close();
        
        if val == 256:
            return JsonResponse({'success': False, 'output': ['Compilation Error: \n {}'.format(log)]})


    f = open('./codes/{}/out.txt'.format(user),'r')
    output = f.read()
    # print(output)
    f.close()
    data = {
        "success": True,
        "output": output
    }
    os.system('rm -f codes/{}/*.txt codes/{}/a.out'.format(user, user, user))
    return JsonResponse(data, status=HTTP_200_OK)
    # return JsonResponse({'error': ['File does not exist']}, status=HTTP_400_BAD_REQUEST)

@api_view(['GET', 'DELETE'])
@authentication_classes([TokenAuthentication])
def display(request, dirk, username, file):
    if dirk == "" or dirk is None:
        dirk = "."
    userId = User.objects.get(username=username).pk
    filepath = username + "/" + dirk
    obj = UserFiles.objects.get(user=userId, filepath=filepath, filename=file)
    serializer = userFilesSerializer(obj)

    fileloc = "./codes/{}/{}".format(filepath, file)
    f = open(fileloc, 'r')
    script = f.read()
    data = {'filename': file, 'script': script}
    try:
        if request.method == 'DELETE':
            os.remove(fileloc)
            obj.delete()
        return JsonResponse(data, status=HTTP_200_OK)
    except:
        return JsonResponse({'error': ['Invalid file reqeust']}, status=HTTP_400_BAD_REQUEST)

def delDir(userId, filepath):
    obj = UserFiles.objects.filter(user=userId, filepath=filepath)
    serializer = userFilesSerializer(obj, many=True)
    directory_content = os.listdir("./codes/{}".format(filepath))
    for x in directory_content:
        if os.path.isdir("./codes/{0}/{1}".format(filepath,x)):
            delDir(userId, filepath + "/" + x)
            os.rmdir("./codes/{0}/{1}".format(filepath, x))
        else:
            fileloc = "./codes/{0}/{1}".format(filepath, x)
            os.remove(fileloc)
    obj.delete()

@api_view(['GET', 'POST', 'DELETE'])
@authentication_classes([TokenAuthentication])
def displayAll(request, dirk, username):
    if dirk == "":
        dirk = "."

    if request.method == 'GET':
        userId = User.objects.get(username=username).pk
        filepath = username + "/" + dirk
        obj = UserFiles.objects.filter(user=userId,filepath=filepath)
        serializer = userFilesSerializer(obj, many=True)
        data = []
        for file in serializer.data:
            f = open("./codes/{}/{}".format(filepath, file['filename']), 'r')
            script = f.read()
            data.append({'filename': file['filename'], 'script': script})

        directory_content = os.listdir("./codes/{}".format(filepath))
        for x in directory_content:
            if os.path.isdir("./codes/{0}/{1}".format(filepath,x)):
                fol_name = x
                data.append({'filename': 'trash.trash', 'script': fol_name})
        return JsonResponse(data, status=HTTP_200_OK, safe=False)

    elif request.method == 'POST':
        script = request.data.get("script")
        filename = request.data.get("filename")
        try:
            data = {"filename": filename, "script": script}
            if not os.path.isdir('./codes'):
                os.mkdir('./codes')
            if not os.path.isdir('./codes/{}'.format(str(username))):
                path = './codes/{}'.format(str(username))
                os.mkdir(path)
            if not os.path.isdir('./codes/{0}/{1}'.format(str(username), str(dirk))):
                path = './codes/{0}/{1}'.format(str(username), str(dirk))
                os.mkdir(path)
                return JsonResponse(data, status=HTTP_200_OK)
            if filename == 'trash.trash':
                return JsonResponse({'error': ['Directory name already exists']}, status=HTTP_400_BAD_REQUEST)

            flag = False
            if not os.path.exists('./codes/{}/{}/{}'.format(username,dirk,filename)):
                flag = True
            f = open('./codes/{}/{}/{}'.format(username,dirk,filename), 'w')
            if script is not None:
                f.write(script)
            
            f.close()
            # url = ('http://127.0.0.1:8000'+'/codes/'+str(filename))
            if flag:
                userId = User.objects.get(username=username).pk
                serializer = userFilesSerializer(data={
                        'user': userId,
                        'filename': filename,
                        'filepath': '{}/{}'.format(username,dirk)
                })

                if serializer.is_valid():
                    serializer.save()
                    return JsonResponse(data, status=HTTP_200_OK)
                return JsonResponse(serializer.errors, status=HTTP_400_BAD_REQUEST, safe=False)
            return JsonResponse(data, status=HTTP_200_OK)

        except:
            return JsonResponse({'error': ['Invalid file reqeust']}, status=HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        userId = User.objects.get(username=username).pk
        filepath = username + "/" + dirk
        delDir(userId, filepath)
        os.rmdir("./codes/{}".format(filepath))
        return JsonResponse({'filename': "success", "script": "success"}, status=HTTP_200_OK)


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