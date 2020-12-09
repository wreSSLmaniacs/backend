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

## Need the following for accepting and using ISO 8601 date string input from frontend
from django.utils.dateparse import parse_datetime

## Need the following for comparision with current datetime using datetime.now(timezone.utc)
from datetime import date, datetime, timezone

## Point Evaluator, currently hyperbolic, we plan to change this to a Gompertz function in a patch
def pointsfromtime(t1,t2,t3):
    total = t3 - t1
    elapsed = t2-t1
    return int(500*total.total_seconds()/elapsed.total_seconds())

# Create your views here.

## All classes authenticated with Token Authentication provided by Django REST Framework TokenAuth

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
def runboard(request):
    """View queries the Contests table for contests running at time of request"""
    if request.method=='GET':
        try:
            ## __lte and __gte methods filter the correct contests
            contests = Contest.objects.filter(starttime__lte = datetime.now(timezone.utc),endtime__gte = datetime.now(timezone.utc))
        except:
            return JsonResponse("error", status=HTTP_404_NOT_FOUND)
        serializer = DateInfoSerializer(contests, many=True) # Uses the detailed serializer for the countdown
        return JsonResponse(serializer.data, safe=False)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
def upboard(request):
    """View queries the Contests table for contests yet to start at time of request"""
    if request.method=='GET':
        try:
            contests = Contest.objects.filter(starttime__gte = datetime.now(timezone.utc))
        except:
            return JsonResponse("error", status=HTTP_404_NOT_FOUND)
        serializer = DateInfoSerializer(contests, many=True) # Uses the detailed serializer for the countdown
        return JsonResponse(serializer.data, safe=False)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
def pastboard(request):
    """View queries the Contests table for contests which are over at time of request"""
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
    """View accepts new competitions into the Contests table"""
    if request.method=='POST':
        title = request.data.get('title')
        problem = request.data.get('problem_st')
        input = request.FILES['infile']
        output = request.FILES['outfile']
        start = parse_datetime(request.data.get('start')) ## django.utils.dateparse.parse_datetime used here
        end = parse_datetime(request.data.get('end'))
        try:
            if start > end: ## Basic check to maintain starttime<endtime in the Contest table
                return JsonResponse("Invalid Time Inputs", safe=False)
            contest = Contest.objects.create(title=title,problem=problem,starttime=start,endtime=end)
            contest.input.save(input.name, input) ## Save the contest files into the local directory with the upload_to method
            contest.output.save(output.name, output) ## Table stores the FileField object
        except:
            return JsonResponse("error", status=HTTP_400_BAD_REQUEST)
        return JsonResponse("Contest created succesfully!", safe=False)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
def getcontest(request,id):
    """View to query the contest table by contest ID"""
    if request.method=='GET':
        try:
            contest = Contest.objects.get(id=id)
        except:
            return JsonResponse("error", status=HTTP_404_NOT_FOUND)
        if contest.starttime>datetime.now(timezone.utc):
            ## To make sure problem statements of upcoming contests are never accessible
            return JsonResponse({
                "title" : "How to Punish Oversmart People",
                "problem": "Attempt the problem when the time comes ye dumb dumb"
            })
        serializer = InfoSerializer(contest)
        return JsonResponse(serializer.data, safe=False)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
def runcode(request,id):
    """View receives code as a string through the editor and runs it, update points on a first successful submission"""
    if request.method=='POST':
        
        user = request.data.get('username')
        code = request.data.get('script')
        lang = request.data.get('language')
        
        try:
            contest = Contest.objects.get(id=id)
        except:
            return JsonResponse("error", status=HTTP_404_NOT_FOUND)
        
        ## Frontend has measures to not send responses to past/future contests
        ## This is a supporting backend check
        sub = datetime.now(timezone.utc)
        if contest.starttime>sub or contest.endtime<sub:
            return JsonResponse("Submission made to depricated contest, discarded!",safe=False)

        ## Please make sure the codes/temp/ directory exists in the Root directory while using this view

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

        if lang=='ruby':
            os.system('touch ./codes/temp/{}/code.rb'.format(user))
            c = open('./codes/temp/{}/code.rb'.format(user),'w')
            c.write(code)
            c.close()
            os.system('cp {} ./codes/temp/{}/in.txt'.format(contest.input.path,user))
            os.system('cp {} ./codes/temp/{}/out.txt'.format(contest.output.path,user))
            if os.system('ruby ./codes/temp/{}/code.rb < ./codes/temp/{}/in.txt > ./codes/temp/{}/myout.txt'.format(user,user,user)):
                os.system('rm -rf ./codes/temp/{}'.format(user))
                return JsonResponse("Compilation Error", safe=False)
            if os.system('cmp ./codes/temp/{}/out.txt ./codes/temp/{}/myout.txt'.format(user,user)):
                check=False
        
        os.system('rm -rf ./codes/temp/{}'.format(user))
        
        ## The directories are always removed after code is executed, this keeps the storage light and lets us support indefinite submissions

        """The following is the logic for updating ContestUser and PointsTable on a successful submission"""
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
    """View receives file and language, runs it, update points on a first successful submission"""
    if request.method=='POST':
        
        user = request.data.get('username')
        lang = request.data.get('language')
        code = request.FILES['script']

        try:
            contest = Contest.objects.get(id=id)
        except:
            return JsonResponse("error", status=HTTP_404_NOT_FOUND)

        ## Frontend has measures to not send responses to past/future contests
        ## This is a supporting backend check
        sub = datetime.now(timezone.utc)
        if contest.starttime>sub or contest.endtime<sub:
            return JsonResponse("Submission made to depricated contest, discarded!",safe=False)

        ## Please make sure the codes/temp/ directory exists in the Root directory while using this view

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

        if lang=='ruby':
            fs = FileSystemStorage(location='./codes/temp/{}'.format(user))  
            fs.save("code.rb", code)
            os.system('cp {} ./codes/temp/{}/in.txt'.format(contest.input.path,user))
            os.system('cp {} ./codes/temp/{}/out.txt'.format(contest.output.path,user))
            if os.system('ruby ./codes/temp/{}/code.rb < ./codes/temp/{}/in.txt > ./codes/temp/{}/myout.txt'.format(user,user,user)):
                os.system('rm -rf ./codes/temp/{}'.format(user))
                return JsonResponse("Compilation Error", safe=False)
            if os.system('cmp ./codes/temp/{}/out.txt ./codes/temp/{}/myout.txt'.format(user,user)):
                check=False


        os.system('rm -rf ./codes/temp/{}'.format(user))

        ## The directories are always removed after code is executed, this keeps the storage light and lets us support indefinite submissions

        """The following is the logic for updating ContestUser and PointsTable on a successful submission"""
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

"""The runcode and runfile methods can potentially be refactored, we would like to do this in an update"""


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
def getpoints(request,user):
    """View to query for points of a user, when non existent, it creates an entry with 0 points. Used by the profile page."""
    if request.method=='GET':
        try:
            ptable = PointsTable.objects.get(username=user)
        except:
            ptable = PointsTable.objects.create(username=user,points=0)
        return JsonResponse(ptable.points,safe=False)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
def isrunning(request,id):
    """A lightweight view to check if a contest is running, used by the lifecycle hook on a contest's main page."""
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
    """A lightweight view to query a user's points in a particular contest. Used by the contest and pastcontest pages."""
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