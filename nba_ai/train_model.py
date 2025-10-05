import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import MinMaxScaler
import joblib
from predictor.matchup import get_matchup_data  # adjust path as needed


def add_matchup_stats(df):
    # Initialize matchup columns
    df['team1_matchup_wins'] = 0
    df['team2_matchup_wins'] = 0
    df['matchup_total_games'] = 0

    cache = {}

    for idx, row in df.iterrows():
        team1 = row['team1_abbr']
        team2 = row['team2_abbr']
        key = (team1, team2)

        if key not in cache:
            try:
                cache[key] = get_matchup_data(team1, team2)
            except Exception as e:
                print(f"Error fetching matchup for {team1} vs {team2}: {e}")
                cache[key] = None

        stats = cache[key]

        if stats:
            df.at[idx, 'team1_matchup_wins'] = stats['head_to_head']['team1_wins']
            df.at[idx, 'team2_matchup_wins'] = stats['head_to_head']['team2_wins']
            df.at[idx, 'matchup_total_games'] = stats['head_to_head']['total_games']
        else:
            df.at[idx, 'team1_matchup_wins'] = 0
            df.at[idx, 'team2_matchup_wins'] = 0
            df.at[idx, 'matchup_total_games'] = 0

    # Calculate matchup win percentages safely
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

        # Back-to-back
        'team1_back_to_back', 'team2_back_to_back',

        #rest days
        'team1_days_rest', 'team2_days_rest',

        #win streak

        'team1_streak', 'team2_streak',
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
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    print("\nEvaluating model...")
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    print(f"Model Accuracy: {accuracy:.3f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    print("\nSaving model and scaler...")
    joblib.dump(model, 'nba_predictor_model.pkl')
    joblib.dump(scaler, 'nba_scaler.pkl')  # Save scaler too
    print("Model saved to nba_predictor_model.pkl")
    print("Scaler saved to nba_scaler.pkl")