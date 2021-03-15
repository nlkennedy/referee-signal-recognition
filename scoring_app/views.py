from django.shortcuts import render
from django.http.response import StreamingHttpResponse
from scoring_app.camera import VideoCamera
from .models import Teams, Players, TeamMatches, Matches, Games
from django.core import serializers
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import re 
import numpy as np
import cv2
from django.views import View
import os
from functools import reduce

specialChars = re.compile('[@_!#$%^&*()<>?/\|}{~:=]')

class Assets(View):
    def get(self, _request, filename):
        path = os.path.join(os.path.dirname(__file__), 'static', filename)

        if os.path.isfile(path):
            with open(path, 'rb') as file:
                return HttpResponse(file.read(), content_type='application/javascript')
        else:
            return HttpResponseNotFound()

specialChars = re.compile('[@_!#$%^&*()<>?/\|}{~:=]')
done = False 
def representsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

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
    shortened = {
        'let' : 'let',
        'nolet' : 'nlt',
        'stroke' : 'str'  
    }
    check = False
    bgModel = cv2.createBackgroundSubtractorMOG2(0, 50) 

    while True:
        print('calling get frame')
        frame, counter, check, bgModel = camera.get_frame(counter, check, bgModel)
        if frame == -1:
            counter = dict(sorted(counter.items(), key=lambda item: item[1]))
            print('sorted ', counter)
            answer = shortened[list(counter)[3]]
            print('Final answer ', answer)
            yield (answer)
            break
        else: 
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
    print('done with gen')
    return 'Hi!!'

def video_feed(request):
    result = StreamingHttpResponse(gen(VideoCamera()),
                content_type='multipart/x-mixed-replace; boundary=frame')
    # if done:
    #     result = HttpResponse("HELLO")

    return result

@csrf_exempt
def teams(request):
    if request.method == 'GET':
        queryset = Teams.objects.all()
        data = serializers.serialize('json', queryset)
        return HttpResponse(data, content_type='application/json')
    elif request.method == 'POST':
        try:
            body = request.body.decode('utf-8')
            json_body = json.loads(body)
            #Verify Name
            if (specialChars.search(json_body['team_name']) != None):
                return HttpResponse(status=400)

            Teams.objects.create(team_name=json_body['team_name'])
        except:
            return HttpResponse(status=500)
        return HttpResponse(status=201)

@csrf_exempt
def players(request):
    if request.method == 'GET':
        body = request.body.decode('utf-8')
        json_body = json.loads(body)
        #Verify Id
        if not representsInt(json_body['team_id']):
            return HttpResponse(status=400)

        queryset = Players.objects.all().filter(team_id=json_body['team_id'])
        data = serializers.serialize('json', queryset)
        return HttpResponse(data, content_type='application/json')
    elif request.method == 'POST':
        try:
            body = request.body.decode('utf-8')
            json_body = json.loads(body)

            #Verify Data
            if not representsInt(json_body['team_id']):
                return HttpResponse(status=400)

            if (specialChars.search(json_body['name']) != None):
                return HttpResponse(status=400)

            Players.objects.create(
                team_id=Teams.objects.get(pk=json_body['team_id']),
                name=json_body['name']
            )
        except:
            return HttpResponse(status=500)
        return HttpResponse(status=201)

@csrf_exempt
def teammatches(request):
    if request.method == 'GET':
        queryset = TeamMatches.objects.all()
        data = serializers.serialize('json', queryset)
        return HttpResponse(data, content_type='application/json')
    elif request.method == 'POST':
        try:
            body = request.body.decode('utf-8')
            json_body = json.loads(body)

            #Verify ids
            if (not representsInt(json_body['home_team_id'])) or (not representsInt(json_body['away_team_id'])):
                return HttpResponse(status=400)

            TeamMatches.objects.create(
                home_team_id=Teams.objects.get(pk=json_body['home_team_id']),
                away_team_id=Teams.objects.get(pk=json_body['away_team_id']),
            )
        except:
            return HttpResponse(status=500)
        return HttpResponse(status=201)

@csrf_exempt
def teammatches_all(request):
    if request.method == 'POST':
        try:
            body = request.body.decode('utf-8')
            data = json.loads(body)

            #Make sure there are no special characters in data passed from user
            if specialChars.search(data['home_team_name']) != None:
                return HttpResponse(status=400)
            if specialChars.search(data['away_team_name']) != None:
                return HttpResponse(status=400)
            # create teams
            home_team = Teams.objects.create(team_name=data['home_team_name'])
            away_team = Teams.objects.create(team_name=data['away_team_name'])

            # create teammatch
            team_match = TeamMatches.objects.create(
                home_team_id=home_team,
                away_team_id=away_team,
            )

            for match in data['matches']: 
                # Verify no special characters
                if (specialChars.search(match['home_player']) != None):
                    return HttpResponse(status=400)
                if (specialChars.search(match['away_player']) != None):
                    return HttpResponse(status=400)
                #Verify data
                if (not representsInt(match['match_rank'])):
                    return HttpResponse(status=400)
                if (not representsInt(match['court_number'])):
                    return HttpResponse(status=400)   

                # create players
                home_player = Players.objects.create(team_id=home_team, name=match['home_player'])
                away_player = Players.objects.create(team_id=away_team, name=match['away_player'])

                # create match
                Matches.objects.create(
                    team_match_id=team_match,
                    home_player_id=home_player,
                    away_player_id=away_player,
                    match_rank=match['match_rank'],
                    court_number=match['court_number']
                )

            data = json.dumps({"team_match_id": team_match.pk})
            return HttpResponse(data, content_type='application/json')
        except:
            return HttpResponse(status=500)
    return HttpResponse(status=201)

@csrf_exempt
def teammatches_summary(request):
    if request.method == 'GET':
        try:
            teammatches = TeamMatches.objects.all()
            summary = []
            for teammatch in teammatches:             
                entry = {
                    "pk": teammatch.pk,
                    "home_team_name": teammatch.home_team_id.team_name,
                    "away_team_name": teammatch.away_team_id.team_name,
                    "date_played": str(teammatch.date_played),
                    "done": teammatch.done
                }
                summary.append(entry)

            data = json.dumps(summary)
            return HttpResponse(data, content_type='application/json')
        except:
            return HttpResponse(status=500)

@csrf_exempt
def matches(request):
    if request.method == 'GET':
        team_match_id = request.GET['team_match_id']

        #Verify ID  
        if not representsInt(team_match_id):
            return HttpResponse(status=400)

        queryset = Matches.objects.all().filter(team_match_id=team_match_id)
        data = serializers.serialize('json', queryset)
        return HttpResponse(data, content_type='application/json')
    elif request.method == 'POST':
        try:
            body = request.body.decode('utf-8')
            json_body = json.loads(body)
            #Verify Ids 
            if (not representsInt(json_body['team_match_id'])):
                return HttpResponse(status=400)
            if (not representsInt(json_body['home_player_id'])):
                return HttpResponse(status=400)
            if (not representsInt(json_body['away_player_id'])):
                return HttpResponse(status=400)
            #Verify data
            if (not representsInt(json_body['match_rank'])):
                return HttpResponse(status=400)
            if (not representsInt(json_body['court_number'])):
                return HttpResponse(status=400)   

            Matches.objects.create(
                team_match_id=TeamMatches.objects.get(pk=json_body['team_match_id']),
                home_player_id=Players.objects.get(pk=json_body['home_player_id']),
                away_player_id=Players.objects.get(pk=json_body['away_player_id']),
                match_rank=json_body['match_rank'],
                court_number=json_body['court_number']
            )
        except:
            return HttpResponse(status=500)
        return HttpResponse(status=201)
    elif request.method == 'PATCH':
        try:
            body = request.body.decode('utf-8')
            data = json.loads(body)

            if (not isinstance(data['match_id'], int)):
                return HttpResponse(status=400)

            match = Matches.objects.get(pk=data['match_id'])

            match.home_player_score = data['home_player_score']
            match.away_player_score = data['away_player_score']
            match.done = data['done']
            match.save()

            # check if teammatch is done and update as necesary 
            all_matches = Matches.objects.filter(team_match_id=match.team_match_id.pk)
            team_match_done = reduce(lambda a, b : a & b.done, all_matches, True)
            if team_match_done:
                team_match = match.team_match_id
                team_match.done = team_match_done
                team_match.save()

            response_data = json.dumps({'match_id': match.pk})
            return HttpResponse(response_data, content_type='application/json')
        except: 
            return HttpResponse(status=500)
    return HttpResponse(status=201)


@csrf_exempt
def matches_summary(request):
    if request.method == 'GET':
        try:
            team_match_id = request.GET['team_match_id']

            #Verify ID
            if not representsInt(team_match_id):
                return HttpResponse(status=400)

            teammatch = TeamMatches.objects.get(pk=team_match_id)
            matches = Matches.objects.all().filter(team_match_id=team_match_id)
            match_summary = []

            for match in matches: 
                entry = {
                    "pk": match.pk,
                    "home_player_name": match.home_player_id.name,
                    "away_player_name": match.away_player_id.name,
                    "home_player_score": match.home_player_score,
                    "away_player_score": match.away_player_score,
                    "match_rank": match.match_rank,
                    "court_number": match.court_number,
                    "done": match.done
                }
                match_summary.append(entry)

            data = json.dumps({
                "pk": teammatch.pk,
                "home_team_name": teammatch.home_team_id.team_name,
                "away_team_name": teammatch.away_team_id.team_name,
                "matches": match_summary
            })

            return HttpResponse(data, content_type='application/json')
        except:
            return HttpResponse(status=500)

@csrf_exempt
def games(request):
    if request.method == 'GET':
        game_id = request.GET['game_id']
        
        #Verify ID
        if not representsInt(game_id):
            return HttpResponse(status=400)

        game = Games.objects.get(pk=game_id)

        game_data = {
            'game_id': game.game_id,
            'home_player_score': game.home_player_score,
            'away_player_score': game.away_player_score,
            'game_number': game.game_number,
            'done': game.done
        }

        match_data = {
            'team_match_id': game.match_id.team_match_id.pk,
            'match_id': game.match_id.pk,
            'home_team_name': game.match_id.home_player_id.team_id.team_name,
            'away_team_name': game.match_id.away_player_id.team_id.team_name,
            'home_player_name': game.match_id.home_player_id.name,
            'away_player_name': game.match_id.away_player_id.name,
            'home_player_score': game.match_id.home_player_score,
            'away_player_score': game.match_id.away_player_score,
            'done': game.match_id.done
        }

        data = {
            'game_data': game_data,
            'match_data': match_data
        }

        response_data = json.dumps(data)
        return HttpResponse(response_data, content_type='application/json')
    elif request.method == 'POST':
        try:
            body = request.body.decode('utf-8')
            data = json.loads(body)

            #Verify Id
            if not representsInt(data['match_id']):
                return HttpResponse(status=400)

            game = Games.objects.create(
                match_id=Matches.objects.get(pk=data['match_id']),
                game_number=data['game_number']
            )

            response_data = json.dumps({'game_id': game.pk})
            return HttpResponse(response_data, content_type='application/json')
        except:
            return HttpResponse(status=500)
    elif request.method == 'PATCH':
        try:
            body = request.body.decode('utf-8')
            data = json.loads(body)

            #Verify Id
            if not representsInt(data['game_id']):
                return HttpResponse(status=400)
                
            game = Games.objects.get(pk=data['game_id'])

            game.home_player_score = data['home_player_score']
            game.away_player_score = data['away_player_score']
            game.done = data['done']
            game.save()

            response_data = json.dumps({'game_id': game.pk})
            return HttpResponse(response_data, content_type='application/json')
        except:
            return HttpResponse(status=500)
    return HttpResponse(status=201)

@csrf_exempt
def games_summary(request):
    if request.method == 'GET':
        match_id = request.GET['match_id']

        #Verify Id
        if not representsInt(match_id):
            return HttpResponse(status=400)
                
        games = Games.objects.all().filter(match_id=match_id)
        games_summary = []

        for game in games: 
            entry = {
                "pk": game.pk,
                "home_player_score": game.home_player_score,
                "away_player_score": game.away_player_score,
                "game_number": game.game_number,
                "done": game.done
            }
            games_summary.append(entry)

        data = json.dumps(games_summary)
        return HttpResponse(data, content_type='application/json')





'''



def post_new_game(request):

def update_game(request):

def get_games(request):

def get_summary(request):

'''