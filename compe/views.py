import os
from django.db.models import indexes
from rest_framework.decorators import api_view
from django.http.response import JsonResponse
from rest_framework.status import HTTP_400_BAD_REQUEST

from .models import Contest
from .serializers import InfoSerializer

# Create your views here.

@api_view(['GET'])
def dashboard(request):
    if request.method=='GET':
        try:
            contests = Contest.objects.all()
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
        try:
            contest = Contest.objects.create(title=title,problem=problem)
            contest.input.save(input.name, input)
            contest.output.save(output.name, output)
        except:
            return JsonResponse("error", status=HTTP_400_BAD_REQUEST)
        return JsonResponse("success", safe=False)