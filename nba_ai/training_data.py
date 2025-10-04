from nba_api.stats.endpoints import leaguegamelog
import pandas as pd
import time


def collect_all_games_efficient(seasons=['2022-23', '2023-24', '2024-25']):
    """Efficiently collect all game data"""

    all_training_data = []

    for season in seasons:
        print(f"\n{'=' * 50}")
        print(f"Processing {season} season...")
        print(f"{'=' * 50}")

        # Get ALL games from the season - minimal parameters
        print("Fetching all games...")
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

            team_stats[team_abbr] = {
                'wins': wins,
                'losses': losses,
                'win_pct': win_pct
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

            # Use pre-calculated stats
            team1_stats = team_stats[team1_abbr]
            team2_stats = team_stats[team2_abbr]

            all_training_data.append({
                'team1_abbr': team1_abbr,
                'team2_abbr': team2_abbr,
                'team1_wins': team1_stats['wins'],
                'team1_losses': team1_stats['losses'],
                'team1_win_pct': team1_stats['win_pct'],
                'team2_wins': team2_stats['wins'],
                'team2_losses': team2_stats['losses'],
                'team2_win_pct': team2_stats['win_pct'],
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
        time.sleep(2)  # Pause between seasons

    return pd.DataFrame(all_training_data)


if __name__ == "__main__":
    print("Starting NBA training data collection...")
    print("This will take approximately 5-10 minutes")

    start_time = time.time()

    df = collect_all_games_efficient()

    # Save to CSV
    df.to_csv('nba_training_data.csv', index=False)

    elapsed = time.time() - start_time
    print(f"\n{'=' * 50}")
    print(f"COMPLETE!")
    print(f"{'=' * 50}")
    print(f"Total games collected: {len(df)}")
    print(f"Time elapsed: {elapsed / 60:.1f} minutes")
    print(f"Saved to: nba_training_data.csv")
    print(f"\nNext step: Run 'python train_model.py'")