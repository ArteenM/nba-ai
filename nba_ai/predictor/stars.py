
# Can't make enough API calls to make this work unfortunately.
# Since we would need to get the specific player data for every game for every team for a full season
# aka 82 (games) * 30 (teams) = 2460 API calls. It will not work.

# from nba_api.stats.endpoints import BoxScoreTraditionalV2
# import pandas as pd
# import time
# from requests.exceptions import RequestException, ConnectionError
#
# def get_missing_stars(game_id, team_abbr, top_players, max_retries=3):
#     """
#     Returns the number of 'missing stars' — top players (by PPG, etc.)
#     who are still on the team and did not play in the game.
#
#     - A player is considered 'missing' if:
#         - They are listed under the team on the box score
#         - And their MIN is None or 0:00
#     - If the player is no longer on the team (traded/waived), they are ignored.
#
#     Parameters:
#         game_id (str): Game ID (e.g., '0022200301')
#         team_abbr (str): Team abbreviation (e.g., 'LAL')
#         top_players (dict): Dict mapping team_abbr to list of player names
#         max_retries (int): Max retries on timeout
#
#     Returns:
#         int: Number of top players still on the team who did not play
#     """
#
#     for attempt in range(max_retries):
#         try:
#             boxscore = BoxScoreTraditionalV2(game_id=game_id)
#             players_df = boxscore.get_data_frames()[0]
#
#             # Filter to players on the target team
#             team_players = players_df[players_df['TEAM_ABBREVIATION'] == team_abbr].copy()
#
#             if team_players.empty:
#                 return 0
#
#             # Normalize names
#             team_players['PLAYER_NAME'] = team_players['PLAYER_NAME'].str.strip()
#             team_player_names = set(team_players['PLAYER_NAME'])
#
#             missing_count = 0
#             for player in top_players.get(team_abbr, []):
#                 if player in team_player_names:
#                     # Check their minutes
#                     mins = team_players[team_players['PLAYER_NAME'] == player].iloc[0]['MIN']
#                     if pd.isna(mins) or mins in ['00:00', '0:00', '', 'None']:
#                         missing_count += 1
#                 else:
#                     # Player not on the team anymore — traded or not on the roster
#                     continue  # Don't count them as missing
#
#             return missing_count
#
#         except (RequestException, ConnectionError) as e:
#             print(f"[Retry {attempt + 1}/{max_retries}] Network error for game {game_id}: {e}")
#             time.sleep(2 + attempt * 2)  # Backoff delay
#
#         except Exception as e:
#             print(f"Error fetching boxscore for game {game_id}, team {team_abbr}: {e}")
#             return 0
#
#     print(f"Failed to fetch after {max_retries} retries: game {game_id}")
#     return 0
