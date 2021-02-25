from django.shortcuts import render
from django.http.response import StreamingHttpResponse
from scoring_app.camera import VideoCamera
from .models import Teams, Players, TeamMatches, Matches, Games
from django.core import serializers
from django.http import HttpResponse
import json
import numpy as np
import cv2
# Create your views here.


def index(request):
    return render(request, 'scoring_app/home.html')

def predict_page(request):
    return render(request, 'scoring_app/predict.html')

def gen(camera):
    # keeping track of number of times each prediction is made
    counter = {
        'let' : 0,
        'nolet' : 0,
        'none' : 0,
        'stroke' : 0  
    }
    check = False
    bgModel = cv2.createBackgroundSubtractorMOG2(0, 50) 

    while True:
        print('calling get frame')
        frame, counter, check, bgModel = camera.get_frame(counter, check, bgModel)
        if frame == -1:
            break
        else: 
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
    print('done with gen')

def video_feed(request):
    result = StreamingHttpResponse(gen(VideoCamera()),
                    content_type='multipart/x-mixed-replace; boundary=frame')
    return result 

def teammatches(request):
    if request.method == 'GET':
        queryset = TeamMatches.objects.all()
        data = serializers.serialize('json', queryset)
        return HttpResponse(data, content_type='application/json')
    elif request.method == 'POST':
        return HttpResponse(status=201)

def matches(request):
    if request.method == 'GET':
        body = request.body.decode('utf-8')
        json_body = json.loads(body)
        queryset = Matches.objects.all().filter(team_match_id=json_body['team_match_id'])
        data = serializers.serialize('json', queryset)
        return HttpResponse(data, content_type='application/json')
    elif request.method == 'POST':
        return HttpResponse(status=201)


def games(request):
    if request.method == 'GET':
        body = request.body.decode('utf-8')
        json_body = json.loads(body)
        queryset = Games.objects.all().filter(match_id=json_body['match_id'])
        data = serializers.serialize('json', queryset)
        return HttpResponse(data, content_type='application/json')
    elif request.method == 'POST':
        return HttpResponse(status=201)
    elif request.method == 'PUT':
        return HttpResponse(status=201)
    '''



def post_new_game(request):

def update_game(request):

def get_games(request):

def get_summary(request):

'''