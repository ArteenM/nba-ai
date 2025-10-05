from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import pandas as pd
import numpy as np
import joblib
import os
from django.conf import settings

# Load cached training data, model, and scaler once when server starts
try:
    training_data = pd.read_csv('nba_training_data.csv')
    print(f"Loaded {len(training_data)} cached games")
except:
    training_data = None
    print("No cached training data found")

try:
    model = joblib.load('nba_predictor_model.pkl')
    print("ML Model loaded successfully")
except:
    model = None
    print("ML Model not found")

try:
    scaler = joblib.load('nba_scaler.pkl')
    print("Scaler loaded successfully")
except:
    scaler = None
    print("Scaler not found")


def get_team_stats_from_cache(team_abbr):
    """Get team stats from cached data instead of API"""
    if training_data is None:
        return None

    team1_games = training_data[training_data['team1_abbr'] == team_abbr]
    team2_games = training_data[training_data['team2_abbr'] == team_abbr]

    if team1_games.empty and team2_games.empty:
        return None

    if not team1_games.empty:
        latest = team1_games.iloc[-1]
        return {
            'abbreviation': team_abbr,
            'win_pct': latest['team1_win_pct'],
            'wins': latest['team1_wins'],
            'losses': latest['team1_losses'],
            'recent_win_pct': latest['team1_recent_win_pct'],
            'avg_pts': latest['team1_avg_pts'],
            'avg_pts_allowed': latest['team1_avg_pts_allowed'],
            'fg_pct': latest['team1_fg_pct'],
            'fg3_pct': latest['team1_fg3_pct'],
            'ft_pct': latest['team1_ft_pct'],
            'off_reb': latest['team1_off_reb'],
            'def_reb': latest['team1_def_reb'],
            'turnovers': latest['team1_turnovers'],
            'ast_to_to_ratio': latest['team1_ast_to_to_ratio'],
            'streak': latest['team1_streak'],
            'days_rest': latest['team1_days_rest']
        }
    else:
        latest = team2_games.iloc[-1]
        return {
            'abbreviation': team_abbr,
            'win_pct': latest['team2_win_pct'],
            'wins': latest['team2_wins'],
            'losses': latest['team2_losses'],
            'recent_win_pct': latest['team2_recent_win_pct'],
            'avg_pts': latest['team2_avg_pts'],
            'avg_pts_allowed': latest['team2_avg_pts_allowed'],
            'fg_pct': latest['team2_fg_pct'],
            'fg3_pct': latest['team2_fg3_pct'],
            'ft_pct': latest['team2_ft_pct'],
            'off_reb': latest['team2_off_reb'],
            'def_reb': latest['team2_def_reb'],
            'turnovers': latest['team2_turnovers'],
            'ast_to_to_ratio': latest['team2_ast_to_to_ratio'],
            'streak': latest['team2_streak'],
            'days_rest': latest['team2_days_rest']
        }


def get_head_to_head_from_cache(team1_abbr, team2_abbr):
    """Get head-to-head record from cached data"""
    if training_data is None:
        return {'team1_wins': 0, 'team2_wins': 0, 'total': 0}

    matchups = training_data[
        ((training_data['team1_abbr'] == team1_abbr) & (training_data['team2_abbr'] == team2_abbr)) |
        ((training_data['team1_abbr'] == team2_abbr) & (training_data['team2_abbr'] == team1_abbr))
        ]

    if matchups.empty:
        return {'team1_wins': 0, 'team2_wins': 0, 'total': 0}

    team1_wins = 0
    team2_wins = 0

    for _, game in matchups.iterrows():
        if game['team1_abbr'] == team1_abbr:
            if game['winner'] == 1:
                team1_wins += 1
            else:
                team2_wins += 1
        else:
            if game['winner'] == 1:
                team2_wins += 1
            else:
                team1_wins += 1

    total = len(matchups)
    return {
        'team1_wins': team1_wins,
        'team2_wins': team2_wins,
        'total': total,
        'team1_win_pct': team1_wins / total if total > 0 else 0.5,
        'team2_win_pct': team2_wins / total if total > 0 else 0.5
    }


def convert_to_python(obj):
    """Convert numpy types to Python types for JSON serialization"""
    if isinstance(obj, dict):
        return {k: convert_to_python(v) for k, v in obj.items()}
    elif isinstance(obj, (np.integer, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64)):
        return float(obj)
    else:
        return obj


@csrf_exempt
@require_http_methods(["POST"])
def predict_winner(request):
    try:
        data = json.loads(request.body)
        team1 = data.get('team1')
        team2 = data.get('team2')
        team1_b2b = data.get('team1_back_to_back', 0)
        team2_b2b = data.get('team2_back_to_back', 0)

        if not team1 or not team2:
            return JsonResponse({'error': 'Both teams required'}, status=400)

        team1_stats = get_team_stats_from_cache(team1)
        team2_stats = get_team_stats_from_cache(team2)

        if not team1_stats or not team2_stats:
            return JsonResponse({'error': 'Team data not found in cache'}, status=404)

        h2h = get_head_to_head_from_cache(team1, team2)

        team1_stats = convert_to_python(team1_stats)
        team2_stats = convert_to_python(team2_stats)
        h2h = convert_to_python(h2h)

        if model and scaler:
            # Calculate interaction features
            win_pct_diff = team1_stats['win_pct'] - team2_stats['win_pct']
            pts_differential = (team1_stats['avg_pts'] - team1_stats['avg_pts_allowed']) - \
                               (team2_stats['avg_pts'] - team2_stats['avg_pts_allowed'])
            rest_advantage = team1_stats['days_rest'] - team2_stats['days_rest']
            streak_momentum = team1_stats['streak'] - team2_stats['streak']
            fg_pct_diff = team1_stats['fg_pct'] - team2_stats['fg_pct']
            three_pct_diff = team1_stats['fg3_pct'] - team2_stats['fg3_pct']

            # Build feature array with ALL features (must match training order exactly)
            season_features = [
                team1_stats['win_pct'], team2_stats['win_pct'],
                team1_stats['wins'], team2_stats['wins'],
                team1_stats['losses'], team2_stats['losses'],
                team1_stats['recent_win_pct'], team2_stats['recent_win_pct'],
                team1_stats['avg_pts'], team2_stats['avg_pts'],
                team1_stats['avg_pts_allowed'], team2_stats['avg_pts_allowed'],
                team1_stats['fg_pct'], team2_stats['fg_pct'],
                team1_stats['fg3_pct'], team2_stats['fg3_pct'],
                team1_stats['ft_pct'], team2_stats['ft_pct'],
                team1_stats['off_reb'], team2_stats['off_reb'],
                team1_stats['def_reb'], team2_stats['def_reb'],
                team1_stats['turnovers'], team2_stats['turnovers'],
                team1_stats['ast_to_to_ratio'], team2_stats['ast_to_to_ratio'],
                1, 0,  # team1_home, team2_home
                team1_b2b, team2_b2b,
                team1_stats['days_rest'], team2_stats['days_rest'],
                team1_stats['streak'], team2_stats['streak'],
                # Interaction features
                win_pct_diff,
                pts_differential,
                rest_advantage,
                streak_momentum,
                fg_pct_diff,
                three_pct_diff,
            ]

            matchup_features = [
                h2h['team1_win_pct'],
                h2h['team2_win_pct']
            ]

            season_features_array = np.array(season_features).reshape(1, -1)
            season_features_scaled = scaler.transform(season_features_array)

            X = np.hstack([
                season_features_scaled * 0.9,
                np.array(matchup_features).reshape(1, -1) * 0.1
            ])

            prediction = model.predict(X)[0]
            probabilities = model.predict_proba(X)[0]

            winner = team1 if prediction == 1 else team2
            confidence = float(max(probabilities) * 100)

            return JsonResponse({
                'winner': winner,
                'confidence': round(confidence, 1),
                'model_type': 'ML',
                'team1_win_probability': round(float(probabilities[1]) * 100, 1),
                'team2_win_probability': round(float(probabilities[0]) * 100, 1),
                'team1_stats': team1_stats,
                'team2_stats': team2_stats,
                'head_to_head': h2h
            })
        else:
            winner = team1 if team1_stats['win_pct'] > team2_stats['win_pct'] else team2
            confidence = abs(team1_stats['win_pct'] - team2_stats['win_pct']) * 100

            return JsonResponse({
                'winner': winner,
                'confidence': round(float(confidence), 1),
                'model_type': 'rule-based',
                'team1_stats': team1_stats,
                'team2_stats': team2_stats,
                'head_to_head': h2h
            })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)