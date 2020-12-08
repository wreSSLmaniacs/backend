import os
from rest_framework.decorators import api_view
from django.http.response import JsonResponse
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.status import HTTP_404_NOT_FOUND
from django.core.files.storage import FileSystemStorage

from .models import *
from .serializers import InfoSerializer

from django.utils.dateparse import parse_datetime
from datetime import datetime, timezone

# Create your views here.

@api_view(['GET'])
def runboard(request):
    if request.method=='GET':
        try:
            contests = Contest.objects.filter(starttime__lte = datetime.now(timezone.utc),endtime__gte = datetime.now(timezone.utc))
        except:
            return JsonResponse("error", status=HTTP_404_NOT_FOUND)
        serializer = InfoSerializer(contests, many=True)
        return JsonResponse(serializer.data, safe=False)

@api_view(['GET'])
def upboard(request):
    if request.method=='GET':
        try:
            contests = Contest.objects.filter(starttime__gte = datetime.now(timezone.utc))
        except:
            return JsonResponse("error", status=HTTP_404_NOT_FOUND)
        serializer = InfoSerializer(contests, many=True)
        return JsonResponse(serializer.data, safe=False)

@api_view(['GET'])
def pastboard(request):
    if request.method=='GET':
        try:
            contests = Contest.objects.filter(endtime__lte = datetime.now(timezone.utc))
        except:
            return JsonResponse("error", status=HTTP_404_NOT_FOUND)
        serializer = InfoSerializer(contests, many=True)
        return JsonResponse(serializer.data, safe=False)

@api_view(['POST'])
def newcontest(request):
    if request.method=='POST':
        title = request.data.get('title')
        problem = request.data.get('problem_st')
        input = request.FILES['infile']
        output = request.FILES['outfile']
        start = parse_datetime(request.data.get('start'))
        end = parse_datetime(request.data.get('end'))
        try:
            contest = Contest.objects.create(title=title,problem=problem,starttime=start,endtime=end)
            contest.input.save(input.name, input)
            contest.output.save(output.name, output)
        except:
            return JsonResponse("error", status=HTTP_400_BAD_REQUEST)
        return JsonResponse("Contest created succesfully!", safe=False)

@api_view(['GET'])
def getcontest(request,id):
    if request.method=='GET':
        try:
            contest = Contest.objects.get(id=id)
        except:
            return JsonResponse("error", status=HTTP_404_NOT_FOUND)
        if contest.endtime<datetime.now(timezone.utc):
            return JsonResponse({"title":"This Contest Has Expired!"})
        if contest.starttime>datetime.now(timezone.utc):
            return JsonResponse({"title":"This Contest Hasn't Begun yet!"})
        serializer = InfoSerializer(contest)
        return JsonResponse(serializer.data, safe=False)

@api_view(['POST'])
def runcode(request,id):
    if request.method=='POST':
        
        user = request.data.get('username')
        code = request.data.get('script')
        lang = request.data.get('language')
        
        try:
            contest = Contest.objects.get(id=id)
        except:
            return JsonResponse("error", status=HTTP_404_NOT_FOUND)
        
        os.system('mkdir ./codes/temp/{}'.format(user))
        check = True

        if lang=='c_cpp':
            os.system('touch ./codes/temp/{}/code.cpp'.format(user))
            c = open('./codes/temp/{}/code.cpp'.format(user),'w')
            c.write(code)
            c.close()
            os.system('cp {} ./codes/temp/{}/in.txt'.format(contest.input.path,user))
            os.system('cp {} ./codes/temp/{}/out.txt'.format(contest.output.path,user))
            if os.system('g++ -std=c++17 ./codes/temp/{}/code.cpp -o ./codes/temp/{}/exec'.format(user,user)):
                os.system('rm -rf ./codes/temp/{}'.format(user))
                return JsonResponse("Compilation Error", safe=False)
            os.system('./codes/temp/{}/exec < ./codes/temp/{}/in.txt > ./codes/temp/{}/myout.txt'.format(user,user,user))
            if os.system('cmp ./codes/temp/{}/out.txt ./codes/temp/{}/myout.txt'.format(user,user)):
                check=False

        if lang=='python':
            os.system('touch ./codes/temp/{}/code.py'.format(user))
            c = open('./codes/temp/{}/code.py'.format(user),'w')
            c.write(code)
            c.close()
            os.system('cp {} ./codes/temp/{}/in.txt'.format(contest.input.path,user))
            os.system('cp {} ./codes/temp/{}/out.txt'.format(contest.output.path,user))
            if os.system('python3 ./codes/temp/{}/code.py < ./codes/temp/{}/in.txt > ./codes/temp/{}/myout.txt'.format(user,user,user)):
                os.system('rm -rf ./codes/temp/{}'.format(user))
                return JsonResponse("Compilation Error", safe=False)
            if os.system('cmp ./codes/temp/{}/out.txt ./codes/temp/{}/myout.txt'.format(user,user)):
                check=False
        
        os.system('rm -rf ./codes/temp/{}'.format(user))
        if check:
            return JsonResponse("Your Code Worked!",safe=False)
        else:
            return JsonResponse("Incorrect! Try again (:",safe=False)

@api_view(['POST'])
def runfile(request,id):
    if request.method=='POST':
        
        user = request.data.get('username')
        lang = request.data.get('language')
        code = request.FILES['script']

        print(lang)

        try:
            contest = Contest.objects.get(id=id)
        except:
            return JsonResponse("error", status=HTTP_404_NOT_FOUND)
        
        os.system('mkdir ./codes/temp/{}'.format(user))
        check = True

        if lang=='c_cpp':
            fs = FileSystemStorage(location='./codes/temp/{}'.format(user))  
            fs.save("code.cpp", code)
            os.system('cp {} ./codes/temp/{}/in.txt'.format(contest.input.path,user))
            os.system('cp {} ./codes/temp/{}/out.txt'.format(contest.output.path,user))
            if os.system('g++ -std=c++17 ./codes/temp/{}/code.cpp -o ./codes/temp/{}/exec'.format(user,user)):
                os.system('rm -rf ./codes/temp/{}'.format(user))
                return JsonResponse("Compilation Error", safe=False)
            os.system('./codes/temp/{}/exec < ./codes/temp/{}/in.txt > ./codes/temp/{}/myout.txt'.format(user,user,user))
            if os.system('cmp ./codes/temp/{}/out.txt ./codes/temp/{}/myout.txt'.format(user,user)):
                check=False

        if lang=='python':
            fs = FileSystemStorage(location='./codes/temp/{}'.format(user))  
            fs.save("code.py", code)
            os.system('cp {} ./codes/temp/{}/in.txt'.format(contest.input.path,user))
            os.system('cp {} ./codes/temp/{}/out.txt'.format(contest.output.path,user))
            if os.system('python3 ./codes/temp/{}/code.py < ./codes/temp/{}/in.txt > ./codes/temp/{}/myout.txt'.format(user,user,user)):
                os.system('rm -rf ./codes/temp/{}'.format(user))
                return JsonResponse("Compilation Error", safe=False)
            if os.system('cmp ./codes/temp/{}/out.txt ./codes/temp/{}/myout.txt'.format(user,user)):
                check=False
        
        os.system('rm -rf ./codes/temp/{}'.format(user))
        if check:
            return JsonResponse("Your Code Worked!",safe=False)
        else:
            return JsonResponse("Incorrect! Try again (:",safe=False)