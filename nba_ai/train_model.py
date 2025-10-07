import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import MinMaxScaler
import joblib


def add_matchup_stats(df):
    """Calculate matchup stats from the training data itself (no API calls)"""
    print("Calculating head-to-head records from existing game data...")

    df['team1_matchup_wins'] = 0
    df['team2_matchup_wins'] = 0
    df['matchup_total_games'] = 0

    # For each unique team pair, calculate their h2h record
    for idx, row in df.iterrows():
        team1 = row['team1_abbr']
        team2 = row['team2_abbr']

        # Find all games between these two teams
        matchups = df[
            ((df['team1_abbr'] == team1) & (df['team2_abbr'] == team2)) |
            ((df['team1_abbr'] == team2) & (df['team2_abbr'] == team1))
            ]

        team1_wins = 0
        team2_wins = 0

        for _, game in matchups.iterrows():
            if game['team1_abbr'] == team1:
                if game['winner'] == 1:
                    team1_wins += 1
                else:
                    team2_wins += 1
            else:
                if game['winner'] == 1:
                    team2_wins += 1
                else:
                    team1_wins += 1

        df.at[idx, 'team1_matchup_wins'] = team1_wins
        df.at[idx, 'team2_matchup_wins'] = team2_wins
        df.at[idx, 'matchup_total_games'] = len(matchups)

        if idx % 500 == 0:
            print(f"  Processed {idx}/{len(df)} games...")

    # Calculate matchup win percentages
    df['team1_matchup_win_pct'] = np.where(
        df['matchup_total_games'] > 0,
        df['team1_matchup_wins'] / df['matchup_total_games'],
        0.5
    )
    df['team2_matchup_win_pct'] = np.where(
        df['matchup_total_games'] > 0,
        df['team2_matchup_wins'] / df['matchup_total_games'],
        0.5
    )

    return df


if __name__ == "__main__":
    print("Loading training data...")
    df = pd.read_csv('nba_training_data.csv')
    print(f"Loaded {len(df)} games")

    print("Adding matchup data...")
    df = add_matchup_stats(df)

    # Add interaction features
    print("Creating interaction features...")
    df['win_pct_diff'] = df['team1_win_pct'] - df['team2_win_pct']
    df['pts_differential'] = (df['team1_avg_pts'] - df['team1_avg_pts_allowed']) - (
                df['team2_avg_pts'] - df['team2_avg_pts_allowed'])
    df['rest_advantage'] = df['team1_days_rest'] - df['team2_days_rest']
    df['streak_momentum'] = df['team1_streak'] - df['team2_streak']
    df['fg_pct_diff'] = df['team1_fg_pct'] - df['team2_fg_pct']
    df['three_pct_diff'] = df['team1_fg3_pct'] - df['team2_fg3_pct']

    # List of season stats features to use
    season_features = [
        # Win/Loss
        'team1_win_pct', 'team2_win_pct',
        'team1_wins', 'team2_wins',
        'team1_losses', 'team2_losses',

        # Recent performance
        'team1_recent_win_pct', 'team2_recent_win_pct',

        # Scoring
        'team1_avg_pts', 'team2_avg_pts',
        'team1_avg_pts_allowed', 'team2_avg_pts_allowed',

        # Shooting
        'team1_fg_pct', 'team2_fg_pct',
        'team1_fg3_pct', 'team2_fg3_pct',
        'team1_ft_pct', 'team2_ft_pct',

        # Rebounding
        'team1_off_reb', 'team2_off_reb',
        'team1_def_reb', 'team2_def_reb',

        # Ball control
        'team1_turnovers', 'team2_turnovers',
        'team1_ast_to_to_ratio', 'team2_ast_to_to_ratio',

        # Home/Away
        'team1_home', 'team2_home',

        # Back-to-back & rest
        'team1_back_to_back', 'team2_back_to_back',
        'team1_days_rest', 'team2_days_rest',

        # Streak
        'team1_streak', 'team2_streak',

        # Interaction features
        'win_pct_diff',
        'pts_differential',
        'rest_advantage',
        'streak_momentum',
        'fg_pct_diff',
        'three_pct_diff',
    ]

    # Extract season stats features
    X_season = df[season_features].values

    # Normalize season features between 0 and 1
    scaler = MinMaxScaler()
    X_season_scaled = scaler.fit_transform(X_season)

    # Extract matchup head-to-head features
    X_h2h = df[['team1_matchup_win_pct', 'team2_matchup_win_pct']].values

    # Combine with weighted scheme: 90% season stats, 10% matchup stats
    X = np.hstack([
        X_season_scaled * 0.9,
        X_h2h * 0.1
    ])

    y = df['winner'].values

    print("\nSplitting dataset...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("\nTraining model...")
    model = RandomForestClassifier(n_estimators=200, max_depth=20, random_state=42)
    model.fit(X_train, y_train)

    print("\nEvaluating model...")
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    print(f"Model Accuracy: {accuracy:.3f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    print("\nSaving model and scaler...")
    joblib.dump(model, 'nba_predictor_model.pkl')
    joblib.dump(scaler, 'nba_scaler.pkl')
    print("Model saved to nba_predictor_model.pkl")
    print("Scaler saved to nba_scaler.pkl")