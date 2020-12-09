import os
from rest_framework.decorators import api_view, authentication_classes
from django.http.response import JsonResponse
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.status import HTTP_404_NOT_FOUND
from django.core.files.storage import FileSystemStorage
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from .models import *
from .serializers import InfoSerializer, DateInfoSerializer

from django.utils.dateparse import parse_datetime
from datetime import date, datetime, timezone

# Point Evaluator

def pointsfromtime(t1,t2,t3):
    total = t3 - t1
    elapsed = t2-t1
    return int(1000-500*elapsed.total_seconds()/total.total_seconds())

# Create your views here.

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
def runboard(request):
    if request.method=='GET':
        try:
            contests = Contest.objects.filter(starttime__lte = datetime.now(timezone.utc),endtime__gte = datetime.now(timezone.utc))
        except:
            return JsonResponse("error", status=HTTP_404_NOT_FOUND)
        serializer = DateInfoSerializer(contests, many=True)
        return JsonResponse(serializer.data, safe=False)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
def upboard(request):
    if request.method=='GET':
        try:
            contests = Contest.objects.filter(starttime__gte = datetime.now(timezone.utc))
        except:
            return JsonResponse("error", status=HTTP_404_NOT_FOUND)
        serializer = DateInfoSerializer(contests, many=True)
        return JsonResponse(serializer.data, safe=False)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
def pastboard(request):
    if request.method=='GET':
        try:
            contests = Contest.objects.filter(endtime__lte = datetime.now(timezone.utc))
        except:
            return JsonResponse("error", status=HTTP_404_NOT_FOUND)
        serializer = InfoSerializer(contests, many=True)
        return JsonResponse(serializer.data, safe=False)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
def newcontest(request):
    if request.method=='POST':
        title = request.data.get('title')
        problem = request.data.get('problem_st')
        input = request.FILES['infile']
        output = request.FILES['outfile']
        start = parse_datetime(request.data.get('start'))
        end = parse_datetime(request.data.get('end'))
        try:
            if start > end:
                return JsonResponse("Invalid Time Inputs", safe=False)
            contest = Contest.objects.create(title=title,problem=problem,starttime=start,endtime=end)
            contest.input.save(input.name, input)
            contest.output.save(output.name, output)
        except:
            return JsonResponse("error", status=HTTP_400_BAD_REQUEST)
        return JsonResponse("Contest created succesfully!", safe=False)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
def getcontest(request,id):
    if request.method=='GET':
        try:
            contest = Contest.objects.get(id=id)
        except:
            return JsonResponse("error", status=HTTP_404_NOT_FOUND)
        if contest.starttime>datetime.now(timezone.utc):
            return JsonResponse({
                "title" : "How to Punish Oversmart People",
                "problem": "Attempt the problem when the time comes ye dumb dumb"
            })
        serializer = InfoSerializer(contest)
        return JsonResponse(serializer.data, safe=False)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
def runcode(request,id):
    if request.method=='POST':
        
        user = request.data.get('username')
        code = request.data.get('script')
        lang = request.data.get('language')
        
        try:
            contest = Contest.objects.get(id=id)
        except:
            return JsonResponse("error", status=HTTP_404_NOT_FOUND)
        
        sub = datetime.now(timezone.utc)
        if contest.starttime>sub or contest.endtime<sub:
            return JsonResponse("Submission made to depricated contest, discarded!",safe=False)

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
            os.system('./codes/timeout -m 256000 -t 3500 ./codes/temp/{}/exec < ./codes/temp/{}/in.txt > ./codes/temp/{}/myout.txt'.format(user,user,user))
            if os.system('cmp ./codes/temp/{}/out.txt ./codes/temp/{}/myout.txt'.format(user,user)):
                check=False

        if lang=='python':
            os.system('touch ./codes/temp/{}/code.py'.format(user))
            c = open('./codes/temp/{}/code.py'.format(user),'w')
            c.write(code)
            c.close()
            os.system('cp {} ./codes/temp/{}/in.txt'.format(contest.input.path,user))
            os.system('cp {} ./codes/temp/{}/out.txt'.format(contest.output.path,user))
            if os.system('./codes/timeout -m 256000 -t 3500 python3 ./codes/temp/{}/code.py < ./codes/temp/{}/in.txt > ./codes/temp/{}/myout.txt'.format(user,user,user)):
                os.system('rm -rf ./codes/temp/{}'.format(user))
                return JsonResponse("Compilation Error", safe=False)
            if os.system('cmp ./codes/temp/{}/out.txt ./codes/temp/{}/myout.txt'.format(user,user)):
                check=False

        if lang=='ruby':
            os.system('touch ./codes/temp/{}/code.rb'.format(user))
            c = open('./codes/temp/{}/code.rb'.format(user),'w')
            c.write(code)
            c.close()
            os.system('cp {} ./codes/temp/{}/in.txt'.format(contest.input.path,user))
            os.system('cp {} ./codes/temp/{}/out.txt'.format(contest.output.path,user))
            if os.system('./codes/timeout -m 256000 -t 3500 ruby ./codes/temp/{}/code.rb < ./codes/temp/{}/in.txt > ./codes/temp/{}/myout.txt'.format(user,user,user)):
                os.system('rm -rf ./codes/temp/{}'.format(user))
                return JsonResponse("Compilation Error", safe=False)
            if os.system('cmp ./codes/temp/{}/out.txt ./codes/temp/{}/myout.txt'.format(user,user)):
                check=False
        
        os.system('rm -rf ./codes/temp/{}'.format(user))
        
        if check:
            try:
                ContestUser.objects.get(username=user,compe=contest)
                return JsonResponse("You have already passed this contest! Anyway, your Code Works!",safe=False)
            except:
                pts = pointsfromtime(contest.starttime,sub,contest.endtime)
                ContestUser.objects.create(username=user,compe=contest,submittime=sub,points=pts)
                try:
                    ptable = PointsTable.objects.get(username=user)
                except:
                    ptable = PointsTable.objects.create(username=user,points=0)
                ptable.points = ptable.points + pts
                ptable.save()
                return JsonResponse("Your Code Worked! Your points are updated!",safe=False)
        else:
            return JsonResponse("Incorrect! Try again (:",safe=False)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
def runfile(request,id):
    if request.method=='POST':
        
        user = request.data.get('username')
        lang = request.data.get('language')
        code = request.FILES['script']

        try:
            contest = Contest.objects.get(id=id)
        except:
            return JsonResponse("error", status=HTTP_404_NOT_FOUND)

        sub = datetime.now(timezone.utc)
        if contest.starttime>sub or contest.endtime<sub:
            return JsonResponse("Submission made to depricated contest, discarded!",safe=False)


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
            os.system('./codes/timeout -m 256000 -t 3500 ./codes/temp/{}/exec < ./codes/temp/{}/in.txt > ./codes/temp/{}/myout.txt'.format(user,user,user))
            if os.system('cmp ./codes/temp/{}/out.txt ./codes/temp/{}/myout.txt'.format(user,user)):
                check=False

        if lang=='python':
            fs = FileSystemStorage(location='./codes/temp/{}'.format(user))  
            fs.save("code.py", code)
            os.system('cp {} ./codes/temp/{}/in.txt'.format(contest.input.path,user))
            os.system('cp {} ./codes/temp/{}/out.txt'.format(contest.output.path,user))
            if os.system('./codes/timeout -m 256000 -t 3500 python3 ./codes/temp/{}/code.py < ./codes/temp/{}/in.txt > ./codes/temp/{}/myout.txt'.format(user,user,user)):
                os.system('rm -rf ./codes/temp/{}'.format(user))
                return JsonResponse("Compilation Error", safe=False)
            if os.system('cmp ./codes/temp/{}/out.txt ./codes/temp/{}/myout.txt'.format(user,user)):
                check=False

        if lang=='ruby':
            fs = FileSystemStorage(location='./codes/temp/{}'.format(user))  
            fs.save("code.rb", code)
            os.system('cp {} ./codes/temp/{}/in.txt'.format(contest.input.path,user))
            os.system('cp {} ./codes/temp/{}/out.txt'.format(contest.output.path,user))
            if os.system('./codes/timeout -m 256000 -t 3500 ruby ./codes/temp/{}/code.rb < ./codes/temp/{}/in.txt > ./codes/temp/{}/myout.txt'.format(user,user,user)):
                os.system('rm -rf ./codes/temp/{}'.format(user))
                return JsonResponse("Compilation Error", safe=False)
            if os.system('cmp ./codes/temp/{}/out.txt ./codes/temp/{}/myout.txt'.format(user,user)):
                check=False


        os.system('rm -rf ./codes/temp/{}'.format(user))

        if check:
            try:
                ContestUser.objects.get(username=user,compe=contest)
                return JsonResponse("You have already passed this contest! Anyway, your Code Works!",safe=False)
            except:
                pts = pointsfromtime(contest.starttime,sub,contest.endtime)
                ContestUser.objects.create(username=user,compe=contest,submittime=sub,points=pts)
                try:
                    ptable = PointsTable.objects.get(username=user)
                except:
                    ptable = PointsTable.objects.create(username=user,points=0)
                ptable.points = ptable.points + pts
                ptable.save()
                return JsonResponse("Your Code Worked! Your points are updated!",safe=False)
        else:
            return JsonResponse("Incorrect! Try again (:",safe=False)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
def getpoints(request,user):
    if request.method=='GET':
        try:
            ptable = PointsTable.objects.get(username=user)
        except:
            ptable = PointsTable.objects.create(username=user,points=0)
        return JsonResponse(ptable.points,safe=False)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
def isrunning(request,id):
    if request.method=='GET':
        try:
            contest = Contest.objects.get(id=id)
        except:
            return JsonResponse("error", status=HTTP_404_NOT_FOUND)
        t = datetime.now(timezone.utc)
        if t<contest.starttime or t>contest.endtime:
            return JsonResponse(False,safe=False)
        return JsonResponse(True,safe=False)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
def passedpoints(request,user,id):
    if request.method=='GET':
        try:
            contest = Contest.objects.get(id=id)
        except:
            return JsonResponse({"error":"Invalid contest ID"}, status=HTTP_400_BAD_REQUEST)
        try:
            cu = ContestUser.objects.get(username=user,compe=contest)
        except:
            return JsonResponse({
                "passed": False
            })
        return JsonResponse({
            "passed": True,
            "points": cu.points
        })