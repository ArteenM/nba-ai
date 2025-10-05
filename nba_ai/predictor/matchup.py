import pandas as pd
import os
from nba_api.stats.static import teams


def get_team_season_stats(team_abbr, seasons):
    """Load all cached games, add WL if missing, and filter by team abbreviation."""
    file = 'nba_training_data.csv'

    if not os.path.exists(file):
        raise FileNotFoundError(f"File {file} not found")

    df = pd.read_csv(file)

    # Add WL column if missing, based on team1_score and team2_score
    if 'WL' not in df.columns:
        if 'team1_score' in df.columns and 'team2_score' in df.columns:
            df['WL'] = df.apply(
                lambda row: 'W' if row['team1_score'] > row['team2_score'] else 'L',
                axis=1
            )
        else:
            raise ValueError("No 'WL' column or score columns ('team1_score', 'team2_score') found to derive it.")

    # Filter games where this team was playing (either team1 or team2)
    team_games = df[(df['team1_abbr'] == team_abbr) | (df['team2_abbr'] == team_abbr)]

    return team_games


def get_matchup_data(team1_abbr, team2_abbr, seasons=['2022-23', '2023-24', '2024-25']):
    """Get head-to-head and overall stats for two teams."""

    team1_games = get_team_season_stats(team1_abbr, seasons)
    team2_games = get_team_season_stats(team2_abbr, seasons)

    # Calculate team1 wins and losses from both perspectives
    team1_wins = (team1_games[(team1_games['team1_abbr'] == team1_abbr) & (team1_games['WL'] == 'W')]).shape[0] + \
                 (team1_games[(team1_games['team2_abbr'] == team1_abbr) & (team1_games['WL'] == 'L')]).shape[0]

    team1_losses = (team1_games[(team1_games['team1_abbr'] == team1_abbr) & (team1_games['WL'] == 'L')]).shape[0] + \
                   (team1_games[(team1_games['team2_abbr'] == team1_abbr) & (team1_games['WL'] == 'W')]).shape[0]

    team1_win_pct = team1_wins / (team1_wins + team1_losses)

    # Calculate team2 wins and losses
    team2_wins = (team2_games[(team2_games['team1_abbr'] == team2_abbr) & (team2_games['WL'] == 'W')]).shape[0] + \
                 (team2_games[(team2_games['team2_abbr'] == team2_abbr) & (team2_games['WL'] == 'L')]).shape[0]

    team2_losses = (team2_games[(team2_games['team1_abbr'] == team2_abbr) & (team2_games['WL'] == 'L')]).shape[0] + \
                   (team2_games[(team2_games['team2_abbr'] == team2_abbr) & (team2_games['WL'] == 'W')]).shape[0]

    team2_win_pct = team2_wins / (team2_wins + team2_losses)

    # Get team info from nba_api
    team1_info = next(t for t in teams.get_teams() if t['abbreviation'] == team1_abbr)
    team2_info = next(t for t in teams.get_teams() if t['abbreviation'] == team2_abbr)

    # Head-to-head games (where both teams played each other)
    h2h_games = team1_games[
        ((team1_games['team1_abbr'] == team1_abbr) & (team1_games['team2_abbr'] == team2_abbr)) |
        ((team1_games['team1_abbr'] == team2_abbr) & (team1_games['team2_abbr'] == team1_abbr))
    ]

    h2h_team1_wins = (
        (h2h_games['team1_abbr'] == team1_abbr) & (h2h_games['WL'] == 'W')
    ).sum() + (
        (h2h_games['team2_abbr'] == team1_abbr) & (h2h_games['WL'] == 'L')
    ).sum()

    h2h_team2_wins = len(h2h_games) - h2h_team1_wins

    return {
        'team1': {
            'name': team1_info['full_name'],
            'abbreviation': team1_abbr,
            'wins': int(team1_wins),
            'losses': int(team1_losses),
            'win_percentage': round(float(team1_win_pct), 3)
        },
        'team2': {
            'name': team2_info['full_name'],
            'abbreviation': team2_abbr,
            'wins': int(team2_wins),
            'losses': int(team2_losses),
            'win_percentage': round(float(team2_win_pct), 3)
        },
        'head_to_head': {
            'team1_wins': int(h2h_team1_wins),
            'team2_wins': int(h2h_team2_wins),
            'total_games': int(len(h2h_games))
        },
        'seasons_analyzed': seasons
    }


if __name__ == "__main__":
    # Example usage for testing
    team1 = 'LAL'  # Boston Celtics
    team2 = 'BOS'  # Miami Heat
    seasons = ['2022-23', '2023-24', '2024-25']  # Just for compatibility

    try:
        result = get_matchup_data(team1, team2, seasons)
        if result:
            print(result['head_to_head']['team1_wins'])
        else:
            print("Failed to retrieve matchup data. Check team abbreviations.")
    except FileNotFoundError as e:
        print(f"Cache file not found: {e}")
    except ValueError as e:
        print(f"Value error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
