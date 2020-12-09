from django.http.response import JsonResponse
from rest_framework.status import *
from rest_framework.views import APIView
from django.shortcuts import render
from rest_framework import exceptions
from django.http import HttpResponse
from rest_framework.decorators import api_view, authentication_classes
from projects.models import *
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import User, Group
from rest_framework.parsers import JSONParser, FileUploadParser, MultiPartParser, DjangoMultiPartParser, FormParser
from projects.serializers import *
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
import os

# Helper Function 


def delDir(userId, filepath):
    """
    Recursive function for deleting a complete folder and internal contents for user and updating information in database    
    """
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

def renameDir(userId, filepath, newPath):
    """
    Recursive function for renaming a folder and updating relevant paths in database   
    """
    UserFiles.objects.filter(user=userId, filepath=filepath).update(filepath = newPath)
    directory_content = os.listdir("./codes/{}".format(newPath))
    for x in directory_content:
        if os.path.isdir("./codes/{0}/{1}".format(newPath,x)):
            renameDir(userId, filepath + "/" + x, newPath + "/" + x)

# Create your views here.

## All classes authenticated with Token Authentication provided by Django REST Framework TokenAuth

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
def compile(request, username, dirk):
	'''
    Compiles code (language: c++, python, ruby)

    Input: 
    username - 
        Username
        string type
        Format: [a-zA-Z0-9]+
        not NULL 
    dirk - 
        Directory Path
        string type
        Format: [a-zA-Z0-9/_ ]+
        NULL possible

    Compiles relevant code inside a docker container
    '''
    if dirk=="":
		dirk="."
	
	script = request.data.get("script")
	language = request.data.get("language")
	inp = request.data.get("input")
	user = request.data.get("username")

	if not os.path.exists('codes/{}'.format(user)):
	    os.system('mkdir ./codes/{}'.format(user))

	if not os.path.exists('codes/{}/{}'.format(user,dirk)):
	    os.system('mkdir ./codes/{}/{}'.format(user,dirk))
	    
    '''Manages compilation of codes inside directory'''
	filepath = user + "/" + dirk
	os.system('touch ./codes/{}/in.txt'.format(filepath))
	os.system('touch ./codes/{}/out.txt'.format(filepath))
	os.system('touch ./codes/{}/code_temp.cpp'.format(filepath))
	os.system('touch ./codes/{}/code_temp.py'.format(filepath))
	os.system('touch ./codes/{}/code_temp.rb'.format(filepath))

	f = open('./codes/{}/in.txt'.format(filepath),'w')
	f.write(inp)
	f.close()
    """
    Docker support for each language.
    For each language a container is created in the directory of the user with the help of pre-built images.
    If there is an existing container we remove the container.
    After creation we execute the container and create a bash shell in the container and run the command.
    After execution of the code the container is stopped.
    """
	if language == 'c_cpp':
        '''C++ 14 compilation: Environment isolation using docker container. Exceptions handled for compilation and runtime errors. Returns output if no error otherwise returns the error.'''
	    g = open('./codes/{}/code_temp.cpp'.format(filepath),'w')
	    g.write(script)
	    g.close()

	    os.system('docker run --name cppbox -v "$(pwd)"/codes/{}/:/code --rm -t -d cppenv'.format(filepath))    # This will start a container
	    val = os.system('docker exec cppbox /bin/sh -c "g++ -std=c++14 code_temp.cpp > log 2>&1; ./a.out < in.txt > out.txt 2>&1"')       # This will execute our commands (inside container)
	    
	    os.system('docker stop cppbox')
	    f = open("./codes/{}/log".format(filepath), "r")
	    f2 = open("./codes/{}/out.txt".format(filepath), "r")
	    log = f.read()
	    log += f2.read()
	    f.close()
	    f2.close()
	    
	    if val == 32512:
	        return JsonResponse({'success': False, 'output': ['Compilation Error:\n {}'.format(log)]})
	    if val == 34816:
	        return JsonResponse({'success': False, 'output': ['Runtime Error: \n'.format(log)]})
	    if val != 0:
	        return JsonResponse({'success': False, 'output': ['Unexpected Error: \n'.format(log)]})

	elif language == 'python':
        '''Python 3.8.5 compilation: Environment isolation using docker container. Exceptions handled for compilation errors. Returns output if no error otherwise returns the error.'''
	    g = open('./codes/{}/code_temp.py'.format(filepath),'w')
	    g.write(script)
	    g.close()
	    
	    os.system('docker run --name pybox -v "$(pwd)"/codes/{}/:/code --rm -t -d pyenv'.format(filepath))    # This will start a container
	    val = os.system('docker exec pybox /bin/sh -c "python3 code_temp.py < in.txt > out.txt 2>&1"')       # This will execute our commands (inside container)
	    
	    os.system('docker stop pybox')
	    f = open("./codes/{}/out.txt".format(filepath), "r")
	    log = f.read();
	    f.close();
	    
	    if val == 256:
	        return JsonResponse({'success': False, 'output': ['Compilation Error:\n {}'.format(log)]})

	elif language == 'ruby':
        '''Ruby 2.7.0 compilation: Environment isolation using docker container. Exceptions handled for compilation errors. Returns output if no error otherwise returns the error.'''
	    g = open('./codes/{}/code_temp.rb'.format(filepath),'w')
	    g.write(script)
	    g.close()
	    
	    os.system('docker run --name rubybox -v "$(pwd)"/codes/{}/:/code --rm -t -d rubyenv'.format(filepath))    # This will start a container
	    val = os.system('docker exec rubybox /bin/sh -c "ruby code_temp.rb < in.txt > out.txt 2>&1"')       # This will execute our commands (inside container)
	    
	    os.system('docker stop rubybox')
	    f = open("./codes/{}/out.txt".format(filepath), "r")
	    log = f.read();
	    f.close();
	    
	    if val == 256:
	        return JsonResponse({'success': False, 'output': ['Compilation Error: \n {}'.format(log)]})


	f = open('./codes/{}/out.txt'.format(filepath),'r')
	output = f.read()
	f.close()
	data = {
	    "success": True,
	    "output": output
	}
	os.system('rm -f codes/{}/*.txt codes/{}/log codes/{}/a.out'.format(filepath, filepath, filepath))
	os.system('rm -f codes/{}/code_temp.py codes/{}/code_temp.rb codes/{}/code_temp.cpp'.format(filepath,filepath,filepath))
	try:
		os.system('rm -rf ./codes/{}/__pycache__'.format(filepath))
	except:
		pass
	return JsonResponse(data, status=HTTP_200_OK)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
def rename(request, username, dirk):
    '''
    Method created to rename input file or folder and update information in database

    Input:
    username - 
        Username
        string type
        Format: [a-zA-Z0-9]+
        not NULL 
    dirk - 
        Directory Path
        string type
        Format: [a-zA-Z0-9/_ ]+
        NULL possible
    '''
    if dirk == "":
        dirk = "."

    isFile = request.data.get('file')
    oldNm = request.data.get('oldName')
    newNm = request.data.get('newName')
    oldName = "./codes/{}/{}/{}".format(username,dirk,oldNm)
    newName = "./codes/{}/{}/{}".format(username,dirk,newNm)
    userId = User.objects.get(username=username).pk
    data = request.data

    try:
        os.rename(oldName, newName)
        if isFile:
            filepath = username + "/" + dirk
            file = UserFiles.objects.get(user=userId,filename=oldNm, filepath=filepath)
            file.filename = newNm
            file.save()
        else:
            if dirk == ".":
                filepath = username
            else:
                filepath = username + "/" + dirk
            newPath = filepath + "/" + newNm
            filepath = filepath + "/" + oldNm
            print(newPath,filepath)
            renameDir(userId,filepath,newPath)
        return JsonResponse(data, status=HTTP_200_OK)
    except:
        return JsonResponse({"Error":"Name already exists"}, status=HTTP_400_BAD_REQUEST)

@api_view(['GET', 'DELETE'])
@authentication_classes([TokenAuthentication])
def display(request, dirk, username, file):
    '''
    Request Operations for a file
        Get File contents
        Delete File
    
    Input:
    username - 
        Username
        string type
        Format: [a-zA-Z0-9]+
        not NULL 
    dirk - 
        Directory Path
        string type
        Format: [a-zA-Z0-9/_ ]+
        NULL possible
    file - 
        Filename 
        string type 
        Format: [a-zA-Z0-9_ ]+.[a-zA-Z0-9_ ]+
        not NULL
    '''
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
            ''' Delete File Operation'''
            os.remove(fileloc)
            obj.delete()
        return JsonResponse(data, status=HTTP_200_OK)
    except:
        return JsonResponse({'error': ['Invalid file reqeust']}, status=HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST', 'DELETE'])
@authentication_classes([TokenAuthentication])
def displayAll(request, dirk, username):
    '''
    Request Operations for a directory
        Get list of names of Folders and File in directory
        Post file inside Folder - add new file or update existing
        Delete Direcotory
    
    Input:
    username - 
        Username
        string type
        Format: [a-zA-Z0-9]+
        not NULL 
    dirk - 
        Directory Path
        string type
        Format: [a-zA-Z0-9/_ ]+
        NULL possible
    '''
    if dirk == "":
        dirk = "."

    if request.method == 'GET':
        ''' Get Operation for getting list of names of all files and folders in directory'''
        userId = User.objects.get(username=username).pk
        filepath = username + "/" + dirk
        if not os.path.isdir('./codes/{}'.format(str(username))):
            path = './codes/{}'.format(str(username))
            os.mkdir(path)

        obj = UserFiles.objects.filter(user=userId,filepath=filepath)
        serializer = userFilesSerializer(obj, many=True)
        data = []
        print(filepath)
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
        ''' Post Operation for adding new file/updating file information to directory'''
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
        ''' Delete Operation for deleting directory and update database'''
        userId = User.objects.get(username=username).pk
        filepath = username + "/" + dirk
        delDir(userId, filepath)
        os.rmdir("./codes/{}".format(filepath))
        return JsonResponse({'filename': "success", "script": "success"}, status=HTTP_200_OK)