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

# @authentication_classes([TokenAuthentication])
@api_view(['POST'])
@permission_classes([IsAuthenticated])
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
    inp = request.data.get("input")

    # user = request.data.get("username")  # Check this
    user = "testuser" # check this

    if not os.path.exists('codes/{}'.format(user)):
        os.system('mkdir ./codes/{}'.format(user))
        
    os.system('touch ./codes/{}/in.txt'.format(user))
    os.system('touch ./codes/{}/out.txt'.format(user))
    os.system('touch ./codes/{}/temp.cpp'.format(user))
    os.system('touch ./codes/{}/temp.py'.format(user))
    os.system('touch ./codes/{}/temp.r'.format(user))
    os.system('touch ./codes/{}/script.sh'.format(user))
    
    f = open('./codes/{}/in.txt'.format(user),'w')
    f.write(inp)
    f.close()

    # Bug here, "g++ temp.cpp" not working inside container
    if language == 'c_cpp':
        g = open('./codes/{}/temp.cpp'.format(user),'w')
        g.write(script)
        g.close()

        os.system('docker run --name cppbox -v "$(pwd)"/codes/{}/:/code --rm -t -d cppenv'.format(user))    # This will start a container
        val = os.system('docker exec cppbox /bin/sh -c "g++ temp.cpp; ./a.out < in.txt > out.txt"')       # This will execute our commands (inside container)
        
        os.system('docker stop cppbox')
        
        if val == 256:
            return JsonResponse({'success': False, 'output': ['Compilation Error']})
        if val == 6:
            return JsonResponse({'success': False, 'output': ['Runtime Error']})

    elif language == 'python':
        g = open('./codes/{}/temp.py'.format(user),'w')
        g.write(script)
        g.close()
        
        os.system('docker run --name pybox -v "$(pwd)"/codes/{}/:/code --rm -t -d pyenv'.format(user))    # This will start a container
        val = os.system('docker exec pybox /bin/sh -c "python3 temp.py < in.txt > out.txt"')       # This will execute our commands (inside container)
        
        os.system('docker stop pybox')
        
        if val == 256:
            return JsonResponse({'success': False, 'output': ['Compilation Error']})

    elif language == 'r':
        g = open('./codes/{}/temp.r'.format(user),'w')
        g.write(script)
        g.close()
        
        os.system('docker run --name rbox -v "$(pwd)"/codes/{}/:/code --rm -t -d renv'.format(user))    # This will start a container
        val = os.system('docker exec pybox /bin/sh -c "r temp.r < in.txt > out.txt"')       # This will execute our commands (inside container)
        
        os.system('docker stop rbox')
        
        if val == 256:
            return JsonResponse({'success': False, 'output': ['Compilation Error']})


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
def display(request, dirk, username, file):
    if dirk == "":
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

@api_view(['GET', 'POST', 'DELETE'])
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

        first = True
        for x in os.walk("./codes/{}".format(filepath)):
            if first:
                first = False;
                continue
            fol_name = x[0].split('/')[-1]
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
        obj = UserFiles.objects.filter(user=userId, filepath=filepath)
        serializer = userFilesSerializer(obj, many=True)
        os.rmdir("./codes/{}".format(filepath))
        obj.delete()
        return JsonResponse({'Sucess': "True"}, status=HTTP_200_OK)


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
