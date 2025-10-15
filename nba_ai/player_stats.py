"""
Basketball Reference scraper using urllib (bypasses Cloudflare)
"""

from urllib.request import urlopen, Request
from bs4 import BeautifulSoup, Comment
import re
import unicodedata, time


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


from bs4 import BeautifulSoup, Comment
from urllib.request import Request, urlopen

def scrape_breference_starters(team_abbr):
    """
    Scrapes Basketball Reference for the 2025 (or 2024) season
    and returns the team's starting 5 player names.
    """
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
def scrape_breference_stats(player_name):
    """
    Scrape Basketball Reference for player stats using urllib
    """
    url = build_bref_url(player_name)
    print(f"Fetching: {url}")
    
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
        
        print("✅ Found stats_pullout div")
        
        # Find all stat boxes (they're in <div class="p1"> or <div class="p2">)
        stat_boxes = stats_pullout.find_all('div', class_=['p1', 'p2', 'p3'])
        #print(stat_boxes)
        print(f"Found {len(stat_boxes)} stat boxes")

        season_stats = {}
        
        for box in soup.find_all('div'):
            label_tag = box.find('span', class_='poptip')
            if not label_tag:
                continue

            short_label = label_tag.find('strong').text.strip()
            values = [p.text.strip() for p in box.find_all('p')]

            if not values:
                continue

            # Only take first <p> = most recent season (2024-25)
            season_stats[short_label] = values[0]
        return season_stats
        
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def find_player_variations(player_name):
    """Try different URL variations (01-09)"""
    for suffix in range(1, 10):
        url = build_bref_url(player_name, suffix)
        if not url:
            continue
        
        print(f"\nTrying: {url}")
        
        try:
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            html = urlopen(req, timeout=5)
            
            # Check if we got a valid page
            soup = BeautifulSoup(html, 'html.parser')
            title = soup.find('title')
            
            if title and 'Page Not Found' not in title.get_text():
                print(f"✅ Found: {url}")
                return url
        except:
            print(f"   Not found")
            continue
    
    return None

def scrape_breference_stats_vs_team(player_name, opponent_abbr):
    """
    Scrape Basketball Reference for player's average stats against a specific team
    Returns data in same format as scrape_breference_stats()
    
    Args:
        player_name: Full player name (e.g., "Stephen Curry")
        opponent_abbr: 3-letter opponent code (e.g., "LAL", "GSW")
    
    Returns:
        Dict like: {'G': '5', 'PTS': '28.4', 'TRB': '5.2', 'AST': '6.8', 'FG%': '45.2', ...}
    """
    url = build_bref_url(player_name)
    print(f"Fetching: {url}")
    print(f"Looking for games vs {opponent_abbr}")
    
    if not url:
        return None
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        req = Request(url, headers=headers)
        html = urlopen(req, timeout=10)
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find the game log table (it's in a comment)
        gamelog_wrapper = soup.find('div', id='all_pgl_basic')
        
        if not gamelog_wrapper:
            print("❌ Could not find game log")
            return None
        
        # Extract commented HTML
        from bs4 import Comment
        comment = gamelog_wrapper.find(string=lambda text: isinstance(text, Comment))
        
        if not comment:
            # Try finding it directly
            gamelog_table = soup.find('table', id='pgl_basic')
        else:
            table_soup = BeautifulSoup(comment, 'html.parser')
            gamelog_table = table_soup.find('table', id='pgl_basic')
        
        if not gamelog_table:
            print("❌ Could not find game log table")
            return None
        
        print("✅ Found game log table")
        
        tbody = gamelog_table.find('tbody')
        if not tbody:
            print("❌ No tbody in game log")
            return None
        
        rows = tbody.find_all('tr')
        
        # Collect stats from games vs opponent
        games_vs_opponent = []
        
        for row in rows:
            # Skip header rows
            if row.get('class') and 'thead' in row.get('class'):
                continue
            
            # Find opponent column
            opp_cell = row.find('td', {'data-stat': 'opp_id'})
            
            if not opp_cell:
                continue
            
            opp_text = opp_cell.get_text(strip=True)
            
            # Check if this game was against the specified opponent
            if opponent_abbr.upper() not in opp_text.upper():
                continue
            
            # Check if player actually played (has minutes)
            mp_cell = row.find('td', {'data-stat': 'mp'})
            if not mp_cell or not mp_cell.get_text(strip=True):
                continue
            
            # Extract all stats
            game_stats = {}
            
            stat_columns = [
                ('pts', 'PTS'),
                ('trb', 'TRB'),
                ('ast', 'AST'),
                ('fg_pct', 'FG%'),
                ('fg3_pct', 'FG3%'),
                ('ft_pct', 'FT%'),
            ]
            
            for data_stat, key in stat_columns:
                cell = row.find('td', {'data-stat': data_stat})
                if cell and cell.get_text(strip=True):
                    try:
                        value = float(cell.get_text(strip=True))
                        game_stats[key] = value
                    except:
                        game_stats[key] = 0
                else:
                    game_stats[key] = 0
            
            games_vs_opponent.append(game_stats)
        
        if not games_vs_opponent:
            print(f"❌ No games found vs {opponent_abbr}")
            return {
                'G': '0',
                'PTS': '0.0',
                'TRB': '0.0',
                'AST': '0.0',
                'FG%': '0.0',
                'FG3%': '0.0',
                'FT%': '0.0'
            }
        
        # Calculate averages in the same format
        num_games = len(games_vs_opponent)
        
        vs_stats = {
            'G': str(num_games),
            'PTS': f"{sum(g['PTS'] for g in games_vs_opponent) / num_games:.1f}",
            'TRB': f"{sum(g['TRB'] for g in games_vs_opponent) / num_games:.1f}",
            'AST': f"{sum(g['AST'] for g in games_vs_opponent) / num_games:.1f}",
            'FG%': f"{sum(g['FG%'] for g in games_vs_opponent) / num_games:.1f}",
            'FG3%': f"{sum(g['FG3%'] for g in games_vs_opponent) / num_games:.1f}",
            'FT%': f"{sum(g['FT%'] for g in games_vs_opponent) / num_games:.1f}",
        }
        
        print(f"✅ Found {num_games} games vs {opponent_abbr}")
        print(f"   Stats: {vs_stats}")
        
        return vs_stats
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    starters=scrape_breference_stats_vs_team('Trae Young', 'NYK')
    print(starters)