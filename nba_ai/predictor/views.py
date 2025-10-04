from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
import json, os, joblib
from .matchup import get_matchup_data

model_path = os.path.join(settings.BASE_DIR, 'nba_predictor_model.pkl')
try:
    ml_model = joblib.load(model_path)
    print(f"ML Model loaded from {model_path}")
except:
    ml_model = None
    print("ML Model not found, using rule-based prediction")

@csrf_exempt
@require_http_methods(["POST"])
def predict_winner(request):
    try:
        data = json.loads(request.body)
        team1 = data.get('team1')
        team2 = data.get('team2')

        if not team1 or not team2:
            return JsonResponse({'error': 'Both teams required'}, status=400)

        # Fetch matchup data
        matchup_data = get_matchup_data(team1, team2)

        if not matchup_data:
            return JsonResponse({'error': 'Could not fetch data'}, status=500)

        # Simple prediction logic
        team1_win_pct = matchup_data['team1']['win_percentage']
        team2_win_pct = matchup_data['team2']['win_percentage']
        team1_h2h = matchup_data['head_to_head']['team1_wins']
        team2_h2h = matchup_data['head_to_head']['team2_wins']

        # Weight: 70% overall record, 30% head-to-head
        team1_score = (team1_win_pct * 0.7) + ((team1_h2h / (team1_h2h + team2_h2h + 0.01)) * 0.3)
        team2_score = (team2_win_pct * 0.7) + ((team2_h2h / (team1_h2h + team2_h2h + 0.01)) * 0.3)

        winner = team1 if team1_score > team2_score else team2
        confidence = abs(team1_score - team2_score) * 100

        return JsonResponse({
            'winner': winner,
            'confidence': round(confidence, 1),
            'matchup_data': matchup_data
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
@csrf_exempt
@require_http_methods(["POST"])
def get_team_matchup(request):
    """Get 3 seasons of data for two teams"""
    try:
        data = json.loads(request.body)
        team1 = data.get('team1')
        team2 = data.get('team2')

        if not team1 or not team2:
            return JsonResponse({'error': 'Both teams required'}, status=400)

        if team1 == team2:
            return JsonResponse({'error': 'Please select different teams'}, status=400)

        # Fetch data from NBA API
        matchup_data = get_matchup_data(team1, team2)

        if not matchup_data:
            return JsonResponse({'error': 'Could not fetch team data'}, status=500)

        return JsonResponse(matchup_data)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)