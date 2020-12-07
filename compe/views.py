import os
from django.db.models import indexes
from rest_framework.decorators import api_view
from django.http.response import JsonResponse
from rest_framework.status import HTTP_400_BAD_REQUEST

from .models import Contest, TestCases
from .serializers import ContestSerializer

# Create your views here.

@api_view(['GET'])
def dashboard(request):
    if request.method=='GET':
        try:
            contests = Contest.objects.all()
        except:
            return JsonResponse("error", status=HTTP_404_NOT_FOUND)
        serializer = ContestSerializer(contests, many=True)
        return JsonResponse(serializer.data, safe=False)

@api_view(['POST'])
def newcontest(request):
    if request.method=='POST':
        title = request.data.get('title')
        problem = request.data.get('problem_st')
        incases = request.data.get('in_tc')
        outcases = request.data.get('out_tc')
        if len(incases)!=len(outcases):
            return JsonResponse("error", status=HTTP_400_BAD_REQUEST)
        try:
            contest = Contest.objects.create(title=title,problem=problem)
            for x in range(len(incases)):
                tc = TestCases.objects.create(contest=contest,index=x,input=incases[x],output=outcases[x])
                tc.save()
        except:
            return JsonResponse("error", status=HTTP_400_BAD_REQUEST)
        return JsonResponse("success", safe=False)