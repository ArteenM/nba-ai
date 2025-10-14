import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import MinMaxScaler
import joblib
import json
import unicodedata

def normalize_name(name):
    """Convert special characters to ASCII"""
    # Remove accents: Vít → Vit, Krejčí → Krejci
    nfd = unicodedata.normalize('NFD', name)
    return ''.join(c for c in nfd if unicodedata.category(c) != 'Mn').replace(' ', '_')

def add_matchup_stats(df):
    """Calculate matchup stats from the training data itself (no API calls)"""
    print("Calculating head-to-head records from existing game data...")

    df['team1_matchup_wins'] = 0
    df['team2_matchup_wins'] = 0
    df['matchup_total_games'] = 0

    for idx, row in df.iterrows():
        team1 = row['team1_abbr']
        team2 = row['team2_abbr']

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

    # --- VECTORIZE MISSING STARTERS ---
    print("Vectorizing missing starters...")

    for col in ['team1_missing_starters', 'team2_missing_starters']:
        df[col] = df[col].fillna('')
        df[col] = df[col].apply(lambda x: [p.strip() for p in str(x).split(',') if p.strip() != ''])

    # Get all unique missing players
    all_missing_players = set()
    for col in ['team1_missing_starters', 'team2_missing_starters']:
        df[col].apply(lambda x: all_missing_players.update(x))
    all_missing_players = sorted(all_missing_players)

    # Create multi-hot columns
    multi_hot_df = pd.DataFrame(
        0,
        index=df.index,
        columns=[f'{normalize_name(p)}' for p in all_missing_players]
    )
    for player in all_missing_players:
        col_name = f'{normalize_name(player).replace(" ", "_")}'
        multi_hot_df[col_name] = df.apply(
            lambda row: int(player in row['team1_missing_starters'] or player in row['team2_missing_starters']),
            axis=1
        )

    df = pd.concat([df, multi_hot_df], axis=1)
    print(f"Created {len(multi_hot_df.columns)} missing starter columns")

    # --- CREATE INTERACTION FEATURES ---
    print("Creating interaction features...")
    df['win_pct_diff'] = df['team1_win_pct'] - df['team2_win_pct']
    df['pts_differential'] = (df['team1_avg_pts'] - df['team1_avg_pts_allowed']) - (
                              df['team2_avg_pts'] - df['team2_avg_pts_allowed'])
    df['rest_advantage'] = df['team1_days_rest'] - df['team2_days_rest']
    df['streak_momentum'] = df['team1_streak'] - df['team2_streak']
    df['fg_pct_diff'] = df['team1_fg_pct'] - df['team2_fg_pct']
    df['three_pct_diff'] = df['team1_fg3_pct'] - df['team2_fg3_pct']

    # --- SEASON FEATURES ---
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
        
        # NEW: Player matchup performance stats
        'team1_lineup_pts_diff_vs_opp', 'team2_lineup_pts_diff_vs_opp',
        'team1_lineup_reb_diff_vs_opp', 'team2_lineup_reb_diff_vs_opp',
        'team1_lineup_ast_diff_vs_opp', 'team2_lineup_ast_diff_vs_opp',
        'team1_lineup_fg_pct_diff_vs_opp', 'team2_lineup_fg_pct_diff_vs_opp',
        'team1_lineup_vs_opp_games', 'team2_lineup_vs_opp_games',
    ]

    # Add all multi-hot player columns
    season_features += multi_hot_df.columns.tolist()

    # Extract season stats features
    X_season = df[season_features].values

    # Normalize season features
    scaler = MinMaxScaler()
    X_season_scaled = scaler.fit_transform(X_season)

    # Extract matchup head-to-head features
    X_h2h = df[['team1_matchup_win_pct', 'team2_matchup_win_pct']].values

    # Combine: 85% season stats (including player matchup stats), 15% team matchup stats
    X = np.hstack([X_season_scaled * 0.85, X_h2h * 0.15])
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

    # --- FEATURE IMPORTANCE ---
    print("\nCalculating feature importances...")

    # Combine season_features and H2H features for labeling
    feature_names = season_features + ['team1_matchup_win_pct', 'team2_matchup_win_pct']
    importances = model.feature_importances_

    # Create a DataFrame for all features
    feature_importance_df = pd.DataFrame({
        'feature': feature_names,
        'importance': importances
    }).sort_values(by='importance', ascending=False)

    print("\n" + "="*60)
    print("TOP 30 MOST IMPORTANT FEATURES:")
    print("="*60)
    for idx, row in feature_importance_df.head(30).iterrows():
        print(f"{row['feature']:50s} {row['importance']:.4f}")
    
    # Analyze matchup stat importance
    matchup_features = [
        'team1_lineup_pts_diff_vs_opp', 'team2_lineup_pts_diff_vs_opp',
        'team1_lineup_reb_diff_vs_opp', 'team2_lineup_reb_diff_vs_opp',
        'team1_lineup_ast_diff_vs_opp', 'team2_lineup_ast_diff_vs_opp',
        'team1_lineup_fg_pct_diff_vs_opp', 'team2_lineup_fg_pct_diff_vs_opp',
        'team1_lineup_vs_opp_games', 'team2_lineup_vs_opp_games',
    ]
    
    matchup_importance = feature_importance_df[
        feature_importance_df['feature'].isin(matchup_features)
    ].sort_values(by='importance', ascending=False)
    
    print("\n" + "="*60)
    print("PLAYER MATCHUP FEATURE IMPORTANCE:")
    print("="*60)
    for idx, row in matchup_importance.iterrows():
        print(f"{row['feature']:50s} {row['importance']:.4f}")
    
    total_matchup_importance = matchup_importance['importance'].sum()
    print(f"\nTotal matchup features importance: {total_matchup_importance:.4f}")
    print(f"Percentage of total model: {total_matchup_importance*100:.2f}%")

    # Save feature names for prediction script
    with open('injury_columns.json', 'w') as f:
        json.dump(multi_hot_df.columns.tolist(), f, ensure_ascii=False, indent=2)
    print("\nSaved injury column names to injury_columns.json")
    
    # Save all feature names for debugging
    with open('all_feature_names.json', 'w') as f:
        json.dump(feature_names, f, ensure_ascii=False, indent=2)
    print("Saved all feature names to all_feature_names.json")