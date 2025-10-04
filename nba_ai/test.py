from nba_api.stats.endpoints import leaguegamefinder
from nba_api.stats.static import teams
import pandas as pd
import time


def get_team_id(team_abbreviation):
    """Get NBA team ID from abbreviation"""
    nba_teams = teams.get_teams()
    team = [t for t in nba_teams if t['abbreviation'] == team_abbreviation]
    if team:
        return team[0]['id']
    return None


def get_team_season_stats(team_id, seasons):
    """Get team stats for multiple seasons"""
    all_games = []

    for season in seasons:
        print(f"Fetching {season} season...")
        gamefinder = leaguegamefinder.LeagueGameFinder(
            team_id_nullable=team_id,
            season_nullable=season,
            season_type_nullable='Regular Season'
        )
        games = gamefinder.get_data_frames()[0]
        all_games.append(games)
        time.sleep(0.6)  # Rate limiting

    return pd.concat(all_games, ignore_index=True)


def get_matchup_data(team1_abbr, team2_abbr, seasons=['2021-22', '2022-23', '2023-24']):
    """Get head-to-head and overall stats for two teams"""

    # Get team IDs
    team1_id = get_team_id(team1_abbr)
    team2_id = get_team_id(team2_abbr)

    if not team1_id or not team2_id:
        print("Could not find one or both teams")
        return None

    # Get all games for both teams
    team1_games = get_team_season_stats(team1_id, seasons)
    team2_games = get_team_season_stats(team2_id, seasons)

    # Calculate overall stats
    team1_wins = (team1_games['WL'] == 'W').sum()
    team1_losses = (team1_games['WL'] == 'L').sum()
    team1_win_pct = team1_wins / (team1_wins + team1_losses)

    team2_wins = (team2_games['WL'] == 'W').sum()
    team2_losses = (team2_games['WL'] == 'L').sum()
    team2_win_pct = team2_wins / (team2_wins + team2_losses)

    # Get team names
    team1_info = [t for t in teams.get_teams() if t['abbreviation'] == team1_abbr][0]
    team2_info = [t for t in teams.get_teams() if t['abbreviation'] == team2_abbr][0]

    print(f"\n{team1_info['full_name']} Overall Stats (3 seasons):")
    print(f"  Wins: {team1_wins}")
    print(f"  Losses: {team1_losses}")
    print(f"  Win %: {team1_win_pct:.3f}")

    print(f"\n{team2_info['full_name']} Overall Stats (3 seasons):")
    print(f"  Wins: {team2_wins}")
    print(f"  Losses: {team2_losses}")
    print(f"  Win %: {team2_win_pct:.3f}")

    # Find head-to-head games by matching GAME_IDs
    h2h_games = []
    for _, game in team1_games.iterrows():
        game_id = game['GAME_ID']
        team2_game = team2_games[team2_games['GAME_ID'] == game_id]
        if not team2_game.empty:
            h2h_games.append(game)

    if h2h_games:
        h2h_df = pd.DataFrame(h2h_games)
        h2h_team1_wins = (h2h_df['WL'] == 'W').sum()
        h2h_team2_wins = len(h2h_df) - h2h_team1_wins
        total_h2h = len(h2h_df)

        print(f"\nHead-to-Head Record:")
        print(f"  {team1_info['full_name']}: {h2h_team1_wins} wins")
        print(f"  {team2_info['full_name']}: {h2h_team2_wins} wins")
        print(f"  Total games: {total_h2h}")
    else:
        h2h_team1_wins = 0
        h2h_team2_wins = 0
        total_h2h = 0
        print("\nNo head-to-head games found")

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
            'total_games': int(total_h2h)
        },
        'seasons_analyzed': seasons
    }


# Test it
if __name__ == "__main__":
    result = get_matchup_data("LAL", "BOS")  # Lakers vs Celtics
    print("\n--- Complete ---")