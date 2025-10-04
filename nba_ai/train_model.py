import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
from predictor.matchup import get_matchup_data  # adjust import path as needed

def add_matchup_stats(df):
    # Add columns for matchup data
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

    # Create head-to-head win percentages with safe division
    df['team1_matchup_win_pct'] = np.where(df['matchup_total_games'] > 0,
                                           df['team1_matchup_wins'] / df['matchup_total_games'],
                                           0.5)
    df['team2_matchup_win_pct'] = np.where(df['matchup_total_games'] > 0,
                                           df['team2_matchup_wins'] / df['matchup_total_games'],
                                           0.5)

    return df

if __name__ == "__main__":
    print("Loading training data...")
    df = pd.read_csv('nba_training_data.csv')
    print(f"Loaded {len(df)} games")

    print("Adding matchup data...")
    df = add_matchup_stats(df)

    # Combine features with 80% weight on season stats, 20% on head-to-head matchup win pct
    overall_features = df[['team1_win_pct', 'team2_win_pct', 'team1_wins', 'team2_wins',
                           'team1_losses', 'team2_losses']].values
    h2h_features = df[['team1_matchup_win_pct', 'team2_matchup_win_pct']].values

    X = np.hstack([
        overall_features * 0.8,
        h2h_features * 0.2
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

    print("\nSaving model...")
    joblib.dump(model, 'nba_predictor_model.pkl')
    print("Model saved to nba_predictor_model.pkl")
