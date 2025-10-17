from nba_api.stats.endpoints import leaguegamelog, playergamelogs, playergamelog
from nba_api.stats.static import teams as static_teams, players
import pandas as pd
import numpy as np
import time

def safe_mean(df, col):
    """Return mean of column if exists, else 0"""
    return df[col].mean() if col in df.columns else 0


def get_player_matchup_stats(all_logs, player_name, opponent_team_abbr, current_game_date):
    """
    Calculate how a player performs against a specific opponent vs their season average.
    Returns dict with comparison metrics.
    """
    player_logs = all_logs[all_logs['PLAYER_NAME'] == player_name].copy()
    
    if player_logs.empty:
        return None
    
    # Convert game date to datetime for filtering
    player_logs['GAME_DATE'] = pd.to_datetime(player_logs['GAME_DATE'])
    
    # Only use games BEFORE the current game
    player_logs = player_logs[player_logs['GAME_DATE'] < current_game_date]
    
    if player_logs.empty:
        return None
    
    # Season averages (all games before this one)
    season_pts = safe_mean(player_logs, 'PTS')
    season_reb = safe_mean(player_logs, 'REB')
    season_ast = safe_mean(player_logs, 'AST')
    season_fg_pct = safe_mean(player_logs, 'FG_PCT')
    season_min = safe_mean(player_logs, 'MIN')
    
    # Games against this specific opponent (before current game)
    matchup_logs = player_logs[player_logs['MATCHUP'].str.contains(opponent_team_abbr, na=False)]
    
    if matchup_logs.empty:
        # No previous games against this opponent - return season averages with 0 differential
        return {
            'season_pts': season_pts,
            'season_reb': season_reb,
            'season_ast': season_ast,
            'season_fg_pct': season_fg_pct,
            'season_min': season_min,
            'vs_opp_pts': season_pts,
            'vs_opp_reb': season_reb,
            'vs_opp_ast': season_ast,
            'vs_opp_fg_pct': season_fg_pct,
            'vs_opp_games': 0,
            'pts_diff': 0,
            'reb_diff': 0,
            'ast_diff': 0,
            'fg_pct_diff': 0
        }
    
    # Opponent-specific averages
    opp_pts = safe_mean(matchup_logs, 'PTS')
    opp_reb = safe_mean(matchup_logs, 'REB')
    opp_ast = safe_mean(matchup_logs, 'AST')
    opp_fg_pct = safe_mean(matchup_logs, 'FG_PCT')
    opp_games = len(matchup_logs)
    
    return {
        'season_pts': season_pts,
        'season_reb': season_reb,
        'season_ast': season_ast,
        'season_fg_pct': season_fg_pct,
        'season_min': season_min,
        'vs_opp_pts': opp_pts,
        'vs_opp_reb': opp_reb,
        'vs_opp_ast': opp_ast,
        'vs_opp_fg_pct': opp_fg_pct,
        'vs_opp_games': opp_games,
        'pts_diff': opp_pts - season_pts,  # Positive = performs better vs this team
        'reb_diff': opp_reb - season_reb,
        'ast_diff': opp_ast - season_ast,
        'fg_pct_diff': opp_fg_pct - season_fg_pct
    }


def aggregate_lineup_matchup_stats(lineup, all_logs, opponent_abbr, game_date):
    """
    Aggregate matchup stats for top players in lineup.
    Returns average differentials for the lineup.
    """
    lineup_stats = []
    
    for player in lineup[:5]:  # Top 5 players by minutes
        stats = get_player_matchup_stats(all_logs, player['PLAYER_NAME'], opponent_abbr, game_date)
        if stats:
            lineup_stats.append(stats)
    
    if not lineup_stats:
        return {
            'avg_pts_diff': 0,
            'avg_reb_diff': 0,
            'avg_ast_diff': 0,
            'avg_fg_pct_diff': 0,
            'total_vs_opp_games': 0
        }
    
    return {
        'avg_pts_diff': np.mean([s['pts_diff'] for s in lineup_stats]),
        'avg_reb_diff': np.mean([s['reb_diff'] for s in lineup_stats]),
        'avg_ast_diff': np.mean([s['ast_diff'] for s in lineup_stats]),
        'avg_fg_pct_diff': np.mean([s['fg_pct_diff'] for s in lineup_stats]),
        'total_vs_opp_games': sum([s['vs_opp_games'] for s in lineup_stats])
    }


def get_main_lineup_by_minutes(logs, team_id):
    """Get top 12 players by minutes played"""
    df = logs.get_data_frames()[0]
    team_df = df[df['TEAM_ID'] == team_id]
    team_df = team_df[team_df['MIN'] != '']
    team_df['MIN'] = pd.to_numeric(team_df['MIN'])
    
    minutes_summary = (
        team_df.groupby('PLAYER_NAME', as_index=False)['MIN']
        .sum()
        .sort_values('MIN', ascending=False)    
    )
    
    return minutes_summary.head(12).to_dict(orient='records')


def player_missed_game(player_log_df, game_id):
    player_log_df['Game_ID'] = player_log_df['Game_ID'].astype(str)
    game_id = str(game_id)
    game_stats = player_log_df[player_log_df['Game_ID'] == game_id]
    
    if game_stats.empty:
        return True
    minutes = pd.to_numeric(game_stats.iloc[0]['MIN'], errors='coerce') or 0
    return minutes == 0


def calculate_streak(games_sorted):
    """Calculate current winning/losing streak"""
    if games_sorted.empty:
        return 0
    
    last_result = games_sorted.iloc[-1]['WL']
    streak = 1
    
    for i in range(len(games_sorted) - 2, -1, -1):
        if games_sorted.iloc[i]['WL'] == last_result:
            streak += 1
        else:
            break
    
    return streak if last_result == 'W' else -streak


def get_team_id(team_abbr):
    """Get NBA team ID from abbreviation"""
    nba_teams = static_teams.get_teams()
    team = [t for t in nba_teams if t['abbreviation'] == team_abbr]
    if team:
        return team[0]['id']
    return None


def calculate_team_stats_as_of_date(team_games, game_date, games_df, team_abbr):
    """
    Calculate team stats using only games BEFORE the given date
    
    Args:
        team_games: All games for this team (sorted by date)
        game_date: The date to calculate stats as of
        games_df: All games in the season (for opponent points)
        team_abbr: Team abbreviation
    
    Returns:
        Dict with team stats as of that date
    """
    # Filter to only games BEFORE this game
    prior_games = team_games[team_games['GAME_DATE'] < game_date].copy()
    
    if prior_games.empty:
        # First game of season - return defaults
        return {
            'wins': 0,
            'losses': 0,
            'win_pct': 0.5,
            'recent_win_pct': 0.5,
            'avg_pts': 0,
            'avg_pts_allowed': 0,
            'avg_fg_pct': 0,
            'avg_fg3_pct': 0,
            'avg_ft_pct': 0,
            'avg_off_reb': 0,
            'avg_def_reb': 0,
            'avg_turnovers': 0,
            'assist_turnover_ratio': 0,
            'current_streak': 0,
        }
    
    # Calculate wins/losses up to this point
    wins = (prior_games['WL'] == 'W').sum()
    losses = (prior_games['WL'] == 'L').sum()
    win_pct = wins / (wins + losses) if (wins + losses) > 0 else 0.5
    
    # Recent form (last 5 games before this one)
    recent_games = prior_games.tail(5)
    recent_wins = (recent_games['WL'] == 'W').sum()
    recent_win_pct = recent_wins / len(recent_games) if len(recent_games) > 0 else 0.5
    
    # Averages from prior games only
    avg_pts = prior_games['PTS'].mean() if not prior_games.empty else 0
    
    # Calculate points allowed from opponent scores
    opp_pts_list = []
    for game_id in prior_games['GAME_ID']:
        game_rows = games_df[games_df['GAME_ID'] == game_id]
        opp = game_rows[game_rows['TEAM_ABBREVIATION'] != team_abbr]
        if not opp.empty:
            opp_pts_list.append(opp.iloc[0]['PTS'])
    avg_pts_allowed = np.mean(opp_pts_list) if opp_pts_list else 0
    
    # Shooting stats
    avg_fg_pct = prior_games['FG_PCT'].mean() if 'FG_PCT' in prior_games.columns else 0
    avg_fg3_pct = prior_games['FG3_PCT'].mean() if 'FG3_PCT' in prior_games.columns else 0
    avg_ft_pct = prior_games['FT_PCT'].mean() if 'FT_PCT' in prior_games.columns else 0
    
    # Rebounding
    avg_off_reb = prior_games['OREB'].mean() if 'OREB' in prior_games.columns else 0
    avg_def_reb = prior_games['DREB'].mean() if 'DREB' in prior_games.columns else 0
    
    # Ball control
    avg_turnovers = prior_games['TOV'].mean() if 'TOV' in prior_games.columns else 0
    avg_assists = prior_games['AST'].mean() if 'AST' in prior_games.columns else 0
    assist_turnover_ratio = avg_assists / avg_turnovers if avg_turnovers > 0 else 0
    
    # Current streak as of this date
    current_streak = calculate_streak(prior_games)
    
    return {
        'wins': int(wins),
        'losses': int(losses),
        'win_pct': float(win_pct),
        'recent_win_pct': float(recent_win_pct),
        'avg_pts': float(avg_pts),
        'avg_pts_allowed': float(avg_pts_allowed),
        'avg_fg_pct': float(avg_fg_pct),
        'avg_fg3_pct': float(avg_fg3_pct),
        'avg_ft_pct': float(avg_ft_pct),
        'avg_off_reb': float(avg_off_reb),
        'avg_def_reb': float(avg_def_reb),
        'avg_turnovers': float(avg_turnovers),
        'assist_turnover_ratio': float(assist_turnover_ratio),
        'current_streak': int(current_streak),
    }


def collect_all_games_efficient(seasons=['2023-24', '2024-25']):
    """Efficiently collect all game data with progressive stats"""
    all_training_data = []
    
    for season in seasons:
        logs = playergamelogs.PlayerGameLogs(season_nullable=season)
        
        print(f"\n{'=' * 50}")
        print(f"Processing {season} season...")
        print(f"{'=' * 50}")
        
        try:
            gamelog = leaguegamelog.LeagueGameLog(season=season)
            games_df = gamelog.get_data_frames()[0]
        except Exception as e:
            print(f"Error fetching data: {e}")
            continue
        
        print(f"Fetched {len(games_df)} team-game records")
        
        # Convert GAME_DATE to datetime
        games_df['GAME_DATE'] = pd.to_datetime(games_df['GAME_DATE'])
        
        # Get all player logs once
        all_logs = logs.get_data_frames()[0]
        all_logs['Game_ID'] = all_logs['GAME_ID'].astype(str)
        all_logs['GAME_DATE'] = pd.to_datetime(all_logs['GAME_DATE'])
        
        # Pre-sort all team games for efficiency
        print("Preparing team game histories...")
        team_games_dict = {}
        team_lineups = {}
        
        for team_abbr in games_df['TEAM_ABBREVIATION'].unique():
            team_id = get_team_id(team_abbr)
            team_lineups[team_abbr] = get_main_lineup_by_minutes(logs, team_id)
            
            team_games = games_df[games_df['TEAM_ABBREVIATION'] == team_abbr].copy()
            team_games = team_games.sort_values('GAME_DATE')
            team_games_dict[team_abbr] = team_games
        
        # Process games
        print("Processing games with progressive stats...")
        grouped = games_df.groupby('GAME_ID')
        games_processed = 0
        
        for game_id, game_data in grouped:
            if len(game_data) != 2:
                continue
            
            game_data = game_data.sort_values('TEAM_ID')
            team1 = game_data.iloc[0]
            team2 = game_data.iloc[1]
            
            team1_abbr = team1['TEAM_ABBREVIATION']
            team2_abbr = team2['TEAM_ABBREVIATION']
            game_date = team1['GAME_DATE']
            
            # Calculate stats AS OF this game date (using only prior games)
            team1_stats = calculate_team_stats_as_of_date(
                team_games_dict[team1_abbr], 
                game_date, 
                games_df, 
                team1_abbr
            )
            
            team2_stats = calculate_team_stats_as_of_date(
                team_games_dict[team2_abbr], 
                game_date, 
                games_df, 
                team2_abbr
            )
            
            # Calculate matchup stats (only using games before this date)
            team1_main_starters = team_lineups[team1_abbr]
            team2_main_starters = team_lineups[team2_abbr]
            
            team1_matchup_stats = aggregate_lineup_matchup_stats(
                team1_main_starters, all_logs, team2_abbr, game_date
            )
            team2_matchup_stats = aggregate_lineup_matchup_stats(
                team2_main_starters, all_logs, team1_abbr, game_date
            )
            
            # Track missing starters
            team1_missing_starters = []
            team2_missing_starters = []
            
            for starter in team1_main_starters:
                player_log_df = all_logs[all_logs['PLAYER_NAME'] == starter['PLAYER_NAME']].copy()
                if player_missed_game(player_log_df, game_id):
                    team1_missing_starters.append(starter['PLAYER_NAME'])
            
            for starter in team2_main_starters:
                player_log_df = all_logs[all_logs['PLAYER_NAME'] == starter['PLAYER_NAME']].copy()
                if player_missed_game(player_log_df, game_id):
                    team2_missing_starters.append(starter['PLAYER_NAME'])
            
            # Home/Away
            team1_home = 1 if '@' not in team1['MATCHUP'] else 0
            team2_home = 1 if '@' not in team2['MATCHUP'] else 0
            
            # Days rest and back-to-back
            team1_prev_games = team_games_dict[team1_abbr][
                team_games_dict[team1_abbr]['GAME_DATE'] < game_date
            ]
            
            team1_is_back_to_back = 0
            team1_days_rest = 0
            if not team1_prev_games.empty:
                last_game_date = team1_prev_games.iloc[-1]['GAME_DATE']
                days_diff = (game_date - last_game_date).days
                team1_days_rest = days_diff
                if days_diff == 1:
                    team1_is_back_to_back = 1
            
            team2_prev_games = team_games_dict[team2_abbr][
                team_games_dict[team2_abbr]['GAME_DATE'] < game_date
            ]
            
            team2_is_back_to_back = 0
            team2_days_rest = 0
            if not team2_prev_games.empty:
                last_game_date = team2_prev_games.iloc[-1]['GAME_DATE']
                days_diff = (game_date - last_game_date).days
                team2_days_rest = days_diff
                if days_diff == 1:
                    team2_is_back_to_back = 1
            
            all_training_data.append({
                'team1_abbr': team1_abbr,
                'team2_abbr': team2_abbr,
                
                # Team 1 stats (as of this game date)
                'team1_wins': team1_stats['wins'],
                'team1_losses': team1_stats['losses'],
                'team1_win_pct': team1_stats['win_pct'],
                'team1_recent_win_pct': team1_stats['recent_win_pct'],
                'team1_avg_pts': team1_stats['avg_pts'],
                'team1_avg_pts_allowed': team1_stats['avg_pts_allowed'],
                'team1_fg_pct': team1_stats['avg_fg_pct'],
                'team1_fg3_pct': team1_stats['avg_fg3_pct'],
                'team1_ft_pct': team1_stats['avg_ft_pct'],
                'team1_off_reb': team1_stats['avg_off_reb'],
                'team1_def_reb': team1_stats['avg_def_reb'],
                'team1_turnovers': team1_stats['avg_turnovers'],
                'team1_ast_to_to_ratio': team1_stats['assist_turnover_ratio'],
                'team1_home': team1_home,
                'team1_back_to_back': team1_is_back_to_back,
                'team1_days_rest': team1_days_rest,
                'team1_streak': team1_stats['current_streak'],
                'team1_missing_starters': ', '.join(team1_missing_starters),
                'team1_lineup_pts_diff_vs_opp': team1_matchup_stats['avg_pts_diff'],
                'team1_lineup_reb_diff_vs_opp': team1_matchup_stats['avg_reb_diff'],
                'team1_lineup_ast_diff_vs_opp': team1_matchup_stats['avg_ast_diff'],
                'team1_lineup_fg_pct_diff_vs_opp': team1_matchup_stats['avg_fg_pct_diff'],
                'team1_lineup_vs_opp_games': team1_matchup_stats['total_vs_opp_games'],
                
                # Team 2 stats (as of this game date)
                'team2_wins': team2_stats['wins'],
                'team2_losses': team2_stats['losses'],
                'team2_win_pct': team2_stats['win_pct'],
                'team2_recent_win_pct': team2_stats['recent_win_pct'],
                'team2_avg_pts': team2_stats['avg_pts'],
                'team2_avg_pts_allowed': team2_stats['avg_pts_allowed'],
                'team2_fg_pct': team2_stats['avg_fg_pct'],
                'team2_fg3_pct': team2_stats['avg_fg3_pct'],
                'team2_ft_pct': team2_stats['avg_ft_pct'],
                'team2_off_reb': team2_stats['avg_off_reb'],
                'team2_def_reb': team2_stats['avg_def_reb'],
                'team2_turnovers': team2_stats['avg_turnovers'],
                'team2_ast_to_to_ratio': team2_stats['assist_turnover_ratio'],
                'team2_home': team2_home,
                'team2_back_to_back': team2_is_back_to_back,
                'team2_days_rest': team2_days_rest,
                'team2_streak': team2_stats['current_streak'],
                'team2_missing_starters': ', '.join(team2_missing_starters),
                'team2_lineup_pts_diff_vs_opp': team2_matchup_stats['avg_pts_diff'],
                'team2_lineup_reb_diff_vs_opp': team2_matchup_stats['avg_reb_diff'],
                'team2_lineup_ast_diff_vs_opp': team2_matchup_stats['avg_ast_diff'],
                'team2_lineup_fg_pct_diff_vs_opp': team2_matchup_stats['avg_fg_pct_diff'],
                'team2_lineup_vs_opp_games': team2_matchup_stats['total_vs_opp_games'],
                
                # Game outcome
                'team1_score': int(team1['PTS']),
                'team2_score': int(team2['PTS']),
                'winner': 1 if team1['WL'] == 'W' else 0,
                'season': season,
                'game_date': game_date
            })
            
            games_processed += 1
            if games_processed % 100 == 0:
                print(f"  Processed {games_processed} games...")
        
        print(f"Season {season} complete: {games_processed} games")
        time.sleep(2)
    
    return pd.DataFrame(all_training_data)


if __name__ == "__main__":
    print("Starting NBA training data collection with matchup stats...")
    print("This will take approximately 10-15 minutes")
    
    start_time = time.time()
    df = collect_all_games_efficient()
    df.to_csv('nba_training_data.csv', index=False)
    
    elapsed = time.time() - start_time
    print(f"\n{'=' * 50}")
    print("COMPLETE!")
    print(f"{'=' * 50}")
    print(f"Total games collected: {len(df)}")
    print(f"Time elapsed: {elapsed / 60:.1f} minutes")
    print("Saved to: nba_training_data.csv")
    print("\nNew features added:")
    print("  - Lineup points differential vs opponent")
    print("  - Lineup rebounds differential vs opponent")
    print("  - Lineup assists differential vs opponent")
    print("  - Lineup FG% differential vs opponent")
    print("  - Total games played vs this opponent")
    print("\nNext step: Run 'python train_model.py'")