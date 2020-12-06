from users.models import Users, UserFiles
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
    inp = request.data.get("input")

    # user = request.data.get("username")  # Check this
    user = "testuser" # check this

    if not os.path.exists('codes/{}'.format(user)):
        os.system('mkdir ./codes/{}'.format(user))
        
    os.system('touch ./codes/{}/in.txt'.format(user))
    os.system('touch ./codes/{}/out.txt'.format(user))
    os.system('touch ./codes/{}/temp.cpp'.format(user))
    os.system('touch ./codes/{}/temp.py'.format(user))
    os.system('touch ./codes/{}/script.sh'.format(user))
    
    f = open('./codes/{}/in.txt'.format(user),'w')
    f.write(inp)
    f.close()

    # Bug her, "g++ temp.cpp" not working inside container
    if language == 'c_cpp':
        os.system('chmod +x ./codes/{}/script.sh'.format(user, user, user))
        py_script = 'g++ temp.cpp -o my.out && ./my.out < in.txt > out.txt && echo done > log'
        # py_script = 'g++ temp.cpp; ./a.out < in.txt > out.txt; echo done > log'

        
        g = open('./codes/{}/temp.cpp'.format(user),'w')
        s = open('./codes/{}/script.sh'.format(user),'w')
        g.write(script)
        s.write(py_script)
        g.close()
        s.close()
        
        os.system('docker run --name cppbox -v "$(pwd)"/codes/{}/:/code --rm -t -d cppenv'.format(user))    # This will start a container
        val = os.system('docker exec -d cppbox bash ./script.sh')       # This will execute our commands (inside container)
        
        os.system('docker stop cppbox')
        if val == 256:
            return JsonResponse({'success': False, 'output': ['Compilation Error']})
        if val == 6:
            return JsonResponse({'success': False, 'output': ['Runtime Error']})

    elif language == 'python':
        os.system('chmod +x ./codes/{}/script.sh'.format(user))
        py_script = 'python3 temp.py < in.txt > out.txt'
        
        g = open('./codes/{}/temp.py'.format(user),'w')
        s = open('./codes/{}/script.sh'.format(user),'w')
        g.write(script)
        s.write(py_script)
        g.close()
        s.close()
        
        os.system('docker run --name pybox -v "$(pwd)"/codes/{}/:/code --rm -t -d pyenv'.format(user))    # This will start a container
        val = os.system('docker exec -d pybox bash ./script.sh')       # This will execute our commands (inside container)
        
        os.system('docker stop pybox')
        if val == 256:
            return JsonResponse({'success': False, 'output': ['Compilation Error']})

    elif language == 'java':
        os.system('chmod +x ./codes/{}/script.sh'.format(user, user, user))
        py_script = 'python3 temp.py < in.txt > out.txt'
        
        g = open('./codes/{}/temp.py'.format(user),'w')
        s = open('./codes/{}/script.sh'.format(user),'w')
        g.write(script)
        s.write(py_script)
        g.close()
        s.close()
        
        os.system('docker run --name pybox -v "$(pwd)"/codes/{}/:/code --rm -t -d pyenv'.format(user))    # This will start a container
        val = os.system('docker exec -d pybox bash ./script.sh')       # This will execute our commands (inside container)
        
        os.system('docker stop pybox')
        if val == 256:
            return JsonResponse({'success': False, 'output': ['Compilation Error']})


    f = open('./codes/{}/out.txt'.format(user),'r')
    output = f.read()
    f.close()
    data = {
        "success": True,
        "output": output
    }
    os.system('rm -f codes/{}/*.txt codes/{}/a.out'.format(user, user, user))
    return JsonResponse(data, status=HTTP_200_OK)
    # return JsonResponse({'error': ['File does not exist']}, status=HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def display(request):
    username = request.data.get("username")
    filename = request.data.get("filename")
    userId = User.objects.get(username=username).pk
    obj = UserFiles.objects.get(user=userId, filename=filename)
    serializer = userFilesSerializer(obj)
    f = open(serializer.data['filepath'], 'r')
    script = f.read()
    data = {'filename': filename, 'script': script}
    print(data)
    return JsonResponse(data, status=HTTP_200_OK)

@api_view(['GET'])
def displayAll(request):
    username = request.data.get("username")
    userId = User.objects.get(username=username).pk
    obj = UserFiles.objects.filter(user=userId)
    serializer = userFilesSerializer(obj, many=True)
    return JsonResponse(serializer.data, safe=False)

@api_view(['POST'])
def deleteFile(request):
    username = request.data.get("username")
    filename = request.data.get("filename")

    userId = User.objects.get(username=username).pk
    obj = UserFiles.objects.get(user=userId, filename=filename)
    serializer = userFilesSerializer(obj)
    print(serializer.data['filepath'])
    os.remove(serializer.data['filepath'])
    obj.delete()
    return JsonResponse({"Success":"True"}, status=HTTP_200_OK)



@api_view(['GET','POST'])
def file(request):
    if request.method == 'POST':
        script = request.data.get("script")
        filename = request.data.get("filename")
        username = request.data.get("username")

        try:
            if script is not None:
                if not os.path.isdir('./codes'):
                    os.mkdir('./codes')
                if not os.path.isdir('./codes/{}'.format(str(username))):
                    path = './codes/{}'.format(str(username))
                    os.mkdir(path)
                flag = False
                if not os.path.exists('./codes/{0}/{1}'.format(username,filename)):
                    flag = True
                f = open('./codes/{0}/{1}'.format(username,filename), 'w')
                f.write(script)
                f.close()
                # url = ('http://127.0.0.1:8000'+'/codes/'+str(filename))
                if flag:
                    userId = User.objects.get(username=username).pk
                    serializer = userFilesSerializer(data={
                            'user': userId,
                            'filename': filename,
                            'filepath': './codes/{0}/{1}'.format(username,filename)
                    })

                    if serializer.is_valid():
                        serializer.save()
                        return JsonResponse(serializer.data, status=HTTP_200_OK)
                    return JsonResponse(serializer.errors, status=HTTP_400_BAD_REQUEST, safe=False)
                data = {"filename": filename, "filepath": './codes/{}/{}'.format(username,filename)}
                return JsonResponse(data, status=HTTP_200_OK)

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
    

