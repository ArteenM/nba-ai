"""
Basketball Reference scraper using urllib (bypasses Cloudflare)
"""

from urllib.request import urlopen, Request
from bs4 import BeautifulSoup, Comment
import re
import unicodedata, time
from functools import wraps

def rate_limit(seconds):
    """Decorator to add delay between function calls"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            time.sleep(seconds)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def parse_player_name(player_name):
    """Parse player name into first and last"""
    player_name = player_name.strip()
    parts = player_name.split()
    
    if len(parts) == 0:
        return None, None
    elif len(parts) == 1:
        return parts[0], ""
    elif len(parts) == 2:
        return parts[0], parts[1]
    else:
        suffixes = {'jr', 'jr.', 'sr', 'sr.', 'ii', 'iii', 'iv', 'v'}
        if parts[-1].lower().rstrip('.') in suffixes:
            return parts[0], ' '.join(parts[1:])
        else:
            return parts[0], ' '.join(parts[1:])


def normalize_for_url(name):
    """Remove accents and special characters"""
    nfd = unicodedata.normalize('NFD', name)
    ascii_name = ''.join(c for c in nfd if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-zA-Z\s\'-]', '', ascii_name)


def build_bref_url(player_name, suffix_num=1):
    """Build Basketball Reference URL"""
    normalized = normalize_for_url(player_name)
    first_name, last_name = parse_player_name(normalized)
    
    if not first_name or not last_name:
        return None
    
    first_name = first_name.lower().replace(' ', '').replace("'", '').replace('-', '')
    last_name = last_name.lower().replace(' ', '').replace("'", '').replace('-', '')
    last_name = re.sub(r'\s*(jr|sr|ii|iii|iv|v)\.?$', '', last_name)
    
    first_letter = last_name[0]
    last_first5 = last_name[:5]
    first_first2 = first_name[:2]
    
    return f"https://www.basketball-reference.com/players/{first_letter}/{last_first5}{first_first2}{suffix_num:02d}.html"

def build_bref_split_url(player_name, suffix_num=1):
    normalized = normalize_for_url(player_name)
    first_name, last_name = parse_player_name(normalized)
    
    if not first_name or not last_name:
        return None
    
    first_name = first_name.lower().replace(' ', '').replace("'", '').replace('-', '')
    last_name = last_name.lower().replace(' ', '').replace("'", '').replace('-', '')
    last_name = re.sub(r'\s*(jr|sr|ii|iii|iv|v)\.?$', '', last_name)
    
    first_letter = last_name[0]
    last_first5 = last_name[:5]
    first_first2 = first_name[:2]
    
    return f"https://www.basketball-reference.com/players/{first_letter}/{last_first5}{first_first2}{suffix_num:02d}/splits/2025"


def scrape_breference_starters(team_abbr):
    """
    Scrapes Basketball Reference for the 2025 (or 2024) season
    and returns the team's starting 5 player names.
    """
    time.sleep(2)
    url = f"https://www.basketball-reference.com/teams/{team_abbr}/2025.html#all_totals_stats"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    # Load HTML
    req = Request(url, headers=headers)
    html = urlopen(req, timeout=10)
    soup = BeautifulSoup(html, 'html.parser')

    # Locate the wrapper that holds the commented table

    starters = []
    total_stats = soup.find('div', id='all_totals_stats')
    comment = total_stats.find(string=lambda text: isinstance(text, Comment))
    
    table_soup = BeautifulSoup(comment, 'html.parser')

    table = table_soup.find('div', id='div_totals_stats')

    rows = table.find_all('tr')
    for row in rows:
        stat = row.find('a')
        if (stat):
            name = stat.get_text(strip=True)
            starters.append(name)
        
        if (len(starters) == 5):
            return starters

def scrape_breference_stats(player_name, team):
    """
    Scrape Basketball Reference for player stats using urllib
    """

 # Boston, Toronto, etc...
    time.sleep(2)
    url = find_player_variations(player_name, team)

    print(url)
    
    if not url:
        return None
    
    try:
        # Use urllib instead of requests to bypass Cloudflare
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        req = Request(url, headers=headers)
        html = urlopen(req, timeout=10)
        
        soup = BeautifulSoup(html, 'html.parser')
        
        career_stats = {
            'player_name': player_name,
            'url': url
        }
        
        # Find the stats_pullout div (the stat boxes at top of page)
        stats_pullout = soup.find('div', class_='stats_pullout')
        
        if not stats_pullout:
            print("❌ Could not find stats_pullout div")
            return None
        
        # Find all stat boxes (they're in <div class="p1"> or <div class="p2">)
        stat_boxes = stats_pullout.find_all('div', class_=['p1', 'p2', 'p3'])
        #print(stat_boxes)

        all_stats = {}
        
        for box in soup.find_all('div'):
            label_tag = box.find('span', class_='poptip')
            if not label_tag:
                continue

            short_label = label_tag.find('strong').text.strip()
            values = [p.text.strip() for p in box.find_all('p')]

            if not values:
                continue

            # Only take first <p> = most recent season (2024-25)
            all_stats[short_label] = values[0]

        # Only needed stats for now
        main_stats = {
            'points': float(all_stats['PTS']),
            'assists': float(all_stats['AST']),
            'rebounds': float(all_stats['TRB']),
            'fgpercent': float(all_stats['FG%']) / 100

        }
        return main_stats
        
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def find_player_variations(player_name, team):
    """Try different URL variations (01-09)"""
    for suffix in range(1, 10):
        url = build_bref_url(player_name, suffix)
        if not url:
            continue
        
        print(f"\nTrying: {url}")
        
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urlopen(req, timeout=5)
        
        # Check if we got a valid page
        soup = BeautifulSoup(html, 'html.parser')
        media = soup.find_all('div', id='meta')
        for cell in media:
            name = cell.find_all('p')
            for j in name:
                a_href = j.find('a')
                if (a_href):
                    team_name = a_href.get_text(strip=True)
                    if (team == team_name):
                        return url

    
    return None


def abbr_to_name(team_abbr):

    abbr = team_abbr.upper()
    
    team_map = {
        'ATL': 'Atlanta',
        'BOS': 'Boston',
        'BKN': 'Brooklyn',
        'CHA': 'Charlotte',
        'CHI': 'Chicago',
        'CLE': 'Cleveland',
        'DAL': 'Dallas',
        'DEN': 'Denver',
        'DET': 'Detroit',
        'GSW': 'Golden State',
        'HOU': 'Houston',
        'IND': 'Indiana',
        'LAC': 'LA Clippers',
        'LAL': 'LA Lakers',
        'MEM': 'Memphis',
        'MIA': 'Miami',
        'MIL': 'Milwaukee',
        'MIN': 'Minnesota',
        'NOP': 'New Orleans',
        'NYK': 'New York',
        'OKC': 'Oklahoma City',
        'ORL': 'Orlando',
        'PHI': 'Philadelphia',
        'PHX': 'Phoenix',
        'POR': 'Portland',
        'SAC': 'Sacramento',
        'SAS': 'San Antonio',
        'TOR': 'Toronto',
        'UTA': 'Utah',
        'WAS': 'Washington'
    }
    
    return team_map.get(abbr, abbr)

def city_to_full_name(city_name):
    """
    Convert city name to full team name
    
    Args:
        city_name: City name (e.g., 'Boston', 'Los Angeles', 'Golden State')
    
    Returns:
        Full team name (e.g., 'Boston Celtics', 'Los Angeles Lakers')
    """
    city = city_name.strip()
    
    city_map = {
        'Atlanta': 'Atlanta Hawks',
        'Boston': 'Boston Celtics',
        'Brooklyn': 'Brooklyn Nets',
        'Charlotte': 'Charlotte Hornets',
        'Chicago': 'Chicago Bulls',
        'Cleveland': 'Cleveland Cavaliers',
        'Dallas': 'Dallas Mavericks',
        'Denver': 'Denver Nuggets',
        'Detroit': 'Detroit Pistons',
        'Golden State': 'Golden State Warriors',
        'Houston': 'Houston Rockets',
        'Indiana': 'Indiana Pacers',
        'LA Clippers': 'LA Clippers',
        'LA Lakers': 'Los Angeles Lakers',
        'Memphis': 'Memphis Grizzlies',
        'Miami': 'Miami Heat',
        'Milwaukee': 'Milwaukee Bucks',
        'Minnesota': 'Minnesota Timberwolves',
        'New Orleans': 'New Orleans Pelicans',
        'New York': 'New York Knicks',
        'Oklahoma City': 'Oklahoma City Thunder',
        'Orlando': 'Orlando Magic',
        'Philadelphia': 'Philadelphia 76ers',
        'Phoenix': 'Phoenix Suns',
        'Portland': 'Portland Trail Blazers',
        'Sacramento': 'Sacramento Kings',
        'San Antonio': 'San Antonio Spurs',
        'Toronto': 'Toronto Raptors',
        'Utah': 'Utah Jazz',
        'Washington': 'Washington Wizards'
    }
    
    return city_map.get(city, city)


def scrape_breference_stats_vs_team(player_name, team_name, opp_team_name):

    # opp_team_name must be this:
    # Boston
    # Brooklyn
    # Chicago
    # Cleveland
    # Dallas
    # Denver
    # Detroit
    # Golden State
    # Houston
    # Indiana
    # LA Clippers
    # LA Lakers
    # Memphis
    # Miami
    # Milwaukee
    # Minnesota
    # New York
    # Oklahoma City
    # Orlando
    # Philadelphia
    # Phoenix
    # Portland
    # Sacramento
    # San Antonio
    # Toronto
    # Utah
    # Washington
    time.sleep(2)
    url = find_player_variations(player_name, team_name)
    url = url.replace('.html', '/splits/2025')
    
    if not url:
        return None
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        req = Request(url, headers=headers)
        html = urlopen(req, timeout=10)
        soup = BeautifulSoup(html, 'html.parser')

        # Find all opponent rows (they have data-stat="split_id")
        rows = soup.find_all('tr')
        stats = {}

        for row in rows:
            # Find the opponent cell
            opponent_cell = row.find('a')
            if (opponent_cell):
                name = opponent_cell.get_text(strip=True)
                if (name == opp_team_name):
                    games = row.find('td', {'data-stat':'g'}).get_text(strip=True)
                    points = row.find('td', {'data-stat':'pts_per_g'}).get_text(strip=True)
                    assists = row.find('td', {'data-stat': 'ast_per_g'}).get_text(strip=True)
                    rebounds = row.find('td', {'data-stat':'trb_per_g'}).get_text(strip=True)
                    fgpercent = row.find('td', {'data-stat': 'fg_pct'}).get_text(strip=True)
                    stats = {
                        'games': (games),
                        'points': float(points),
                        'assists': float(assists),
                        'rebounds': float(rebounds),
                        'fgpercent': float(fgpercent)
                    }

                    return stats
        
        # If no matching team found, return default stats
        print(f"⚠️ No games found vs {opp_team_name}")
        return {
            'games': '0',
            'points': 0.0,
            'assists': 0.0,
            'rebounds': 0.0,
            'fgpercent': 0.0
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        # Return default stats instead of 0
        return {
            'games': '0',
            'points': 0.0,
            'assists': 0.0,
            'rebounds': 0.0,
            'fgpercent': 0.0
        }
    

def difference_vs_opp(player_name, team_name, opp_team_name):
    full_name = abbr_to_name(team_name) # Full name of own team
    team_name = city_to_full_name(full_name)
    player_stats = scrape_breference_stats(player_name, team_name)
    player_vs_team_stats = scrape_breference_stats_vs_team(player_name, team_name, opp_team_name)
    
    # Check if both stats were retrieved successfully
    if not player_stats or not player_vs_team_stats:
        print(f"❌ Could not get stats for {player_name}")
        return {
            'games': '0',
            'points': 0.0,
            'assists': 0.0,
            'rebounds': 0.0,
            'fgpercent': 0.0
        }
    
    # Calculate difference
    difference = {
        'games': player_vs_team_stats['games'],
        'points': player_vs_team_stats['points'] - player_stats['points'],
        'assists': player_vs_team_stats['assists'] - player_stats['assists'],
        'rebounds': player_vs_team_stats['rebounds'] - player_stats['rebounds'],
        'fgpercent': player_vs_team_stats['fgpercent'] - player_stats['fgpercent']
    }

    return difference

if __name__ == "__main__":
    player = 'Lebron James'
    team = 'Los Angeles Lakers'
    stats = scrape_breference_stats_vs_team(player, team, "Boston")
    print(stats)

