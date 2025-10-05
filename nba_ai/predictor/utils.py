"""
NBA Data Collection Utilities
"""
import time
from datetime import datetime, timedelta
from django.utils import timezone
from nba_api.stats.static import teams
from nba_api.stats.endpoints import scoreboardv2, leaguegamefinder
from .models import Team, Season, Game


def setup_teams():
    """Populate database with all NBA teams"""
    print("Setting up NBA teams...")

    # Team divisions mapping
    divisions = {
        # Eastern Conference - Atlantic
        'BOS': ('Atlantic', 'East'), 'BRK': ('Atlantic', 'East'), 'NYK': ('Atlantic', 'East'),
        'PHI': ('Atlantic', 'East'), 'TOR': ('Atlantic', 'East'),
        # Eastern Conference - Central
        'CHI': ('Central', 'East'), 'CLE': ('Central', 'East'), 'DET': ('Central', 'East'),
        'IND': ('Central', 'East'), 'MIL': ('Central', 'East'),
        # Eastern Conference - Southeast
        'ATL': ('Southeast', 'East'), 'CHA': ('Southeast', 'East'), 'MIA': ('Southeast', 'East'),
        'ORL': ('Southeast', 'East'), 'WAS': ('Southeast', 'East'),
        # Western Conference - Northwest
        'DEN': ('Northwest', 'West'), 'MIN': ('Northwest', 'West'), 'OKC': ('Northwest', 'West'),
        'POR': ('Northwest', 'West'), 'UTA': ('Northwest', 'West'),
        # Western Conference - Pacific
        'GSW': ('Pacific', 'West'), 'LAC': ('Pacific', 'West'), 'LAL': ('Pacific', 'West'),
        'PHX': ('Pacific', 'West'), 'SAC': ('Pacific', 'West'),
        # Western Conference - Southwest
        'DAL': ('Southwest', 'West'), 'HOU': ('Southwest', 'West'), 'MEM': ('Southwest', 'West'),
        'NOP': ('Southwest', 'West'), 'SAS': ('Southwest', 'West')
    }

    # Get teams from NBA API
    nba_teams = teams.get_teams()

    teams_created = 0
    for team_data in nba_teams:
        division, conference = divisions.get(team_data['abbreviation'], ('Unknown', 'Unknown'))

        # Split full name into city and team name
        full_name_parts = team_data['full_name'].split()
        if len(full_name_parts) > 1:
            name = full_name_parts[-1]
            city = ' '.join(full_name_parts[:-1])
        else:
            name = team_data['full_name']
            city = team_data['city']

        team, created = Team.objects.get_or_create(
            nba_team_id=team_data['id'],
            defaults={
                'name': name,
                'city': city,
                'abbreviation': team_data['abbreviation'],
                'conference': conference,
                'division': division,
            }
        )

        if created:
            teams_created += 1
            print(f"✅ Created: {team.city} {team.name}")
        else:
            print(f"⚪ Already exists: {team.city} {team.name}")

    print(f"\n🏀 Teams setup complete! Created {teams_created} new teams.")
    print(f"📊 Total teams in database: {Team.objects.count()}")
    return Team.objects.count()


def setup_current_season():
    """Set up the current NBA season"""
    print("\n📅 Setting up current season...")

    season, created = Season.objects.get_or_create(
        year='2025-26',
        defaults={
            'start_date': datetime(2025, 10, 20).date(),
            'end_date': datetime(2026, 4, 13).date(),
            'is_current': True
        }
    )

    if created:
        print("✅ Created 2025-26 season")
    else:
        print("⚪ 2025-26 season already exists")

    return season


def get_recent_games(days=7):
    """Get games from recent days"""
    print(f"\n🎯 Fetching games from last {days} days...")

    try:
        season = Season.objects.get(year='2024-25')
    except Season.DoesNotExist:
        print("❌ Season 2024-25 not found. Run setup_current_season() first.")
        return 0

    games_created = 0
    total_games_found = 0

    for days_ago in range(days):
        game_date = (timezone.now() - timedelta(days=days_ago)).date()
        print(f"📅 Checking {game_date}...")

        try:
            # Get scoreboard for the date
            board = scoreboardv2.ScoreboardV2(game_date=game_date.strftime('%m/%d/%Y'))
            games_data = board.get_data_frames()[0]

            if not games_data.empty:
                total_games_found += len(games_data)
                print(f"   Found {len(games_data)} games")

                for _, game_data in games_data.iterrows():
                    try:
                        home_team = Team.objects.get(nba_team_id=game_data['HOME_TEAM_ID'])
                        away_team = Team.objects.get(nba_team_id=game_data['VISITOR_TEAM_ID'])

                        # Parse game date and time
                        game_date_str = game_data['GAME_DATE_EST']
                        game_time = game_data.get('GAMETIME_EST', '7:00 PM')

                        try:
                            # Combine date and time
                            datetime_str = f"{game_date_str} {game_time}"
                            game_datetime = datetime.strptime(datetime_str, '%Y-%m-%d %I:%M %p')
                        except ValueError:
                            # Fallback if time parsing fails
                            game_datetime = datetime.strptime(game_date_str, '%Y-%m-%d')

                        game_datetime = timezone.make_aware(game_datetime)

                        # Determine game status
                        status_text = str(game_data.get('GAME_STATUS_TEXT', '')).lower()
                        if 'final' in status_text:
                            status = 'finished'
                        elif any(word in status_text for word in ['q1', 'q2', 'q3', 'q4', 'ot', 'half']):
                            status = 'live'
                        else:
                            status = 'scheduled'

                        game, created = Game.objects.get_or_create(
                            nba_game_id=str(game_data['GAME_ID']),
                            defaults={
                                'home_team': home_team,
                                'away_team': away_team,
                                'season': season,
                                'game_date': game_datetime,
                                'status': status,
                                'home_score': game_data.get('PTS_HOME') if status == 'finished' else None,
                                'away_score': game_data.get('PTS_AWAY') if status == 'finished' else None,
                            }
                        )

                        if created:
                            games_created += 1
                            score_info = ""
                            if game.home_score and game.away_score:
                                score_info = f" ({game.away_score}-{game.home_score})"
                            print(f"   ✅ {game}{score_info}")

                    except Team.DoesNotExist:
                        print(f"   ❌ Team not found for game {game_data['GAME_ID']}")
                        continue
                    except Exception as e:
                        print(f"   ❌ Error processing game: {e}")
                        continue
            else:
                print(f"   No games found for {game_date}")

            # Be respectful to the API
            time.sleep(0.6)

        except Exception as e:
            print(f"   ❌ Error fetching games for {game_date}: {e}")
            time.sleep(1)
            continue

    print(f"\n🎮 Games collection complete!")
    print(f"📊 Found {total_games_found} total games")
    print(f"✅ Created {games_created} new games")
    print(f"📈 Total games in database: {Game.objects.count()}")
    return games_created


def quick_setup():
    """Run complete quick setup"""
    print("🚀 === NBA Data Quick Setup ===\n")

    # Setup teams
    team_count = setup_teams()
    time.sleep(1)

    # Setup season
    season = setup_current_season()
    time.sleep(1)

    # Get recent games
    games_count = get_recent_games(days=10)

    print("\n🎉 === Setup Complete! ===")
    print(f"🏀 Teams in database: {team_count}")
    print(f"🎮 Games fetched: {games_count}")
    print(f"📅 Season: {season.year}")

    print("\n🔥 Next steps:")
    print("1. Visit http://127.0.0.1:8000/admin/ to see your data")
    print("2. Click on 'Teams' to see all NBA teams")
    print("3. Click on 'Games' to see recent games with scores")
    print("4. Ready to start building predictions!")

    return {
        'teams': team_count,
        'games': games_count,
        'season': season
    }


# Convenience function for Django shell
def run_setup():
    """Easy function to run from Django shell"""
    return quick_setup()