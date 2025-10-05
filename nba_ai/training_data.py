from nba_api.stats.endpoints import leaguegamelog
import pandas as pd
import numpy as np
import time


def safe_mean(df, col):
    """Return mean of column if exists, else 0"""
    return df[col].mean() if col in df.columns else 0

def collect_all_games_efficient(seasons=['2022-23', '2023-24', '2024-25']):
    """Efficiently collect all game data with extended stats"""

    all_training_data = []

    for season in seasons:
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

        # Calculate season stats for each team ONCE
        print("Calculating team statistics...")
        team_stats = {}

        for team_abbr in games_df['TEAM_ABBREVIATION'].unique():
            team_games = games_df[games_df['TEAM_ABBREVIATION'] == team_abbr]

            wins = (team_games['WL'] == 'W').sum()
            losses = (team_games['WL'] == 'L').sum()
            win_pct = wins / (wins + losses) if (wins + losses) > 0 else 0

            # Recent last 5 games win %
            recent_games = team_games.sort_values('GAME_DATE', ascending=False).head(5)
            recent_wins = (recent_games['WL'] == 'W').sum()
            recent_win_pct = recent_wins / 5 if len(recent_games) == 5 else (recent_wins / len(recent_games) if len(recent_games) > 0 else 0)

            # Average points scored and allowed
            avg_pts = safe_mean(team_games, 'PTS')

            # To get points allowed per game, find opponent points for each game
            opp_pts_list = []
            for game_id in team_games['GAME_ID']:
                game_rows = games_df[games_df['GAME_ID'] == game_id]
                opp = game_rows[game_rows['TEAM_ABBREVIATION'] != team_abbr]
                if not opp.empty:
                    opp_pts_list.append(opp.iloc[0]['PTS'])
            avg_pts_allowed = np.mean(opp_pts_list) if opp_pts_list else 0

            # Shooting percentages
            avg_fg_pct = safe_mean(team_games, 'FG_PCT')
            avg_fg3_pct = safe_mean(team_games, 'FG3_PCT')
            avg_ft_pct = safe_mean(team_games, 'FT_PCT')

            # Rebounds
            avg_off_reb = safe_mean(team_games, 'OREB')
            avg_def_reb = safe_mean(team_games, 'DREB')

            # Turnovers and Assist-to-turnover ratio
            avg_turnovers = safe_mean(team_games, 'TOV')
            avg_assists = safe_mean(team_games, 'AST')
            assist_turnover_ratio = avg_assists / avg_turnovers if avg_turnovers > 0 else 0

            back_to_back = team_games.sort_values('TEAM_ABBREVIATION', ascending=False).head(2)
            print(back_to_back)

            team_stats[team_abbr] = {
                'wins': wins,
                'losses': losses,
                'win_pct': win_pct,
                'recent_win_pct': recent_win_pct,
                'avg_pts': avg_pts,
                'avg_pts_allowed': avg_pts_allowed,
                'avg_fg_pct': avg_fg_pct,
                'avg_fg3_pct': avg_fg3_pct,
                'avg_ft_pct': avg_ft_pct,
                'avg_off_reb': avg_off_reb,
                'avg_def_reb': avg_def_reb,
                'avg_turnovers': avg_turnovers,
                'assist_turnover_ratio': assist_turnover_ratio,
            }

        # Group by GAME_ID to match up opponents
        print("Matching up teams per game...")
        grouped = games_df.groupby('GAME_ID')

        games_processed = 0
        for game_id, game_data in grouped:
            if len(game_data) != 2:
                continue

            # Sort to have consistent team1/team2
            game_data = game_data.sort_values('TEAM_ID')
            team1 = game_data.iloc[0]
            team2 = game_data.iloc[1]

            team1_abbr = team1['TEAM_ABBREVIATION']
            team2_abbr = team2['TEAM_ABBREVIATION']

            team1_stats = team_stats[team1_abbr]
            team2_stats = team_stats[team2_abbr]

            # Home/Away indicator: 1 if team1 is home, else 0
            # 'MATCHUP' looks like 'TEAM1 @ TEAM2' for away, or 'TEAM1 vs TEAM2' for home
            team1_home = 1 if '@' not in team1['MATCHUP'] else 0
            team2_home = 1 if '@' not in team2['MATCHUP'] else 0

            all_training_data.append({
                'team1_abbr': team1_abbr,
                'team2_abbr': team2_abbr,

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

                # All the differences (only doing 6 for now).
                # Dropped accuracy by a full percent.

                # 'win_pct_diff': team1_stats['win_pct'] - team2_stats['win_pct'],
                # 'wins_diff': team1_stats['wins'] - team2_stats['wins'],
                # 'losses_diff': team1_stats['losses'] - team2_stats['losses'],
                # 'recent_win_pct_diff': team1_stats['recent_win_pct'] - team2_stats['recent_win_pct'],
                # 'avg_pts_diff': team1_stats['avg_pts'] - team2_stats['avg_pts'],
                # 'avg_pts_allowed_diff': team1_stats['avg_pts_allowed'] - team2_stats['avg_pts_allowed'],
                # 'fg_pct_diff': team1_stats['avg_fg_pct'] - team2_stats['avg_fg_pct'],
                # 'fg3_pct_diff': team1_stats['avg_fg3_pct'] - team2_stats['avg_fg3_pct'],
                # 'ft_pct_diff': team1_stats['avg_ft_pct'] - team2_stats['avg_ft_pct'],
                # 'off_reb_diff': team1_stats['avg_off_reb'] - team2_stats['avg_off_reb'],
                # 'def_reb_diff': team1_stats['avg_def_reb'] - team2_stats['avg_def_reb'],
                # 'turnovers_diff': team1_stats['avg_turnovers'] - team2_stats['avg_turnovers'],
                # 'ast_to_to_ratio_diff': team1_stats['assist_turnover_ratio'] - team2_stats['assist_turnover_ratio'],


                'team1_score': int(team1['PTS']),
                'team2_score': int(team2['PTS']),
                'winner': 1 if team1['WL'] == 'W' else 0,
                'season': season,
                'game_date': team1['GAME_DATE']
            })

            games_processed += 1
            if games_processed % 100 == 0:
                print(f"  Processed {games_processed} games...")

        print(f"Season {season} complete: {games_processed} games")
        time.sleep(2)

    return pd.DataFrame(all_training_data)


if __name__ == "__main__":
    print("Starting NBA training data collection...")
    print("This will take approximately 5-10 minutes")

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
    print("\nNext step: Run 'python train_model.py'")
