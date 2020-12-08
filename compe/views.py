import os
from rest_framework.decorators import api_view
from django.http.response import JsonResponse
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.status import HTTP_404_NOT_FOUND
from django.core.files.storage import FileSystemStorage
from datetime import datetime, timedelta

from .models import *
from .serializers import InfoSerializer, ContestSerializer

# Create your views here.

@api_view(['GET'])
def dashboard(request):
    if request.method=='GET':
        try:
            cur_time = datetime.now()
            contests = Contest.objects.filter(starttime_lte=cur_time, endtime_gte=cur_time)
        except:
            return JsonResponse("error", status=HTTP_404_NOT_FOUND)
        serializer = InfoSerializer(contests, many=True)
        return JsonResponse(serializer.data, safe=False)

@api_view(['GET'])
def upcoming(request):
    if request.method=='GET':
        try:
            ed_time = datetime.now()
            st_time = ed_time + timedelta(minutes=30)
            contests = Contest.objects.filter(starttime_lte=st_time, endtime_gte=ed_time)
        except:
            return JsonResponse("error", status=HTTP_404_NOT_FOUND)
        serializer = InfoSerializer(contests, many=True)
        return JsonResponse(serializer.data, safe=False)

@api_view(['POST'])
def newcontest(request):
    if request.method=='POST':
        title = request.data.get('title')
        problem = request.data.get('problem_st')
        starttime = request.data.get('starttime')
        endtime = request.data.get('endtime')
        input = request.FILES['infile']
        output = request.FILES['outfile']
        try:
            contest = Contest.objects.create(title=title,problem=problem, starttime = starttime, endtime=endtime)
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
        serializer = InfoSerializer(contest)
        return JsonResponse(serializer.data, safe=False)

def run(user,code,lang,id):
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
        if ContestUser.objects.filter(username=user, compe=id).exists():
            return JsonResponse("Your points don't get doubled (:", safe=False)
        else:
            try:
                contest = Contest.objects.get(id=id)
            except:
                return JsonResponse("error", status=HTTP_404_NOT_FOUND)
            tot_timediff = (contest.endtime - contest.starttime).total_seconds()
            submittime = datetime.now()
            timediff = (submittime - contest.starttime).total_seconds()
            points = 10 * tot_timediff/(tot_timediff + 4*timediff)
            ContestUser.objects.create(username=user,compe=id, submittime=submittime,points=points)

            if PointsTable.objects.filter(username=user).exists():
                player = PointsTable.objects.get(username=user)
                player.points = player.points + points
                player.save()
            else:
                PointsTable.objects.create(username=user,points=points)
            return JsonResponse("Your Code Worked!",safe=False)
    else:
        return JsonResponse("Incorrect! Try again (:",safe=False)

@api_view(['POST'])
def runcode(request,id):
    if request.method=='POST':
        
        user = request.data.get('username')
        code = request.data.get('script')
        lang = request.data.get('language')
        run(user,lang,code,id)

@api_view(['POST'])
def runfile(request,id):
    if request.method=='POST':
        
        user = request.data.get('username')
        lang = request.data.get('language')
        code = request.FILES['script']

        print(lang)
        run(user,lang,code,id)