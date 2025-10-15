"""
Fixed ESPN NBA Injury Scraper
Based on actual ESPN HTML structure
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import os

# Get API key if using RapidAPI fallback

_injury_cache = {}
_cache_timestamp = None
CACHE_DURATION = timedelta(hours=6)


def scrape_espn_injuries():
    """
    Scrape ESPN injuries using correct selectors from inspection
    """
    try:
        url = "https://www.espn.com/nba/injuries"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        
        print(f"Fetching {url}...")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        injuries_by_team = {}
        
        # Find all injury table containers
        tables = soup.find_all('div', class_='ResponsiveTable')
        print(f"Found {len(tables)} ResponsiveTable divs")
        
        for table in tables:
            # Get team name from the span with class "injuries__teamName"
            team_span = table.find('span', class_='injuries__teamName')
            if not team_span:
                # Alternative: look for any span with team name pattern
                team_span = table.find('span', class_=lambda x: x and 'teamName' in x)
            
            if not team_span:
                continue
            
            team_name = team_span.get_text(strip=True)
            team_abbr = map_team_name(team_name)
            
            if not team_abbr:
                print(f"  Could not map team: {team_name}")
                continue
            
            # Find tbody
            tbody = table.find('tbody', class_='Table__TBODY')
            if not tbody:
                continue
            
            injuries = []
            rows = tbody.find_all('tr', class_='Table__TR')
            
            for row in rows:
                # Find specific cells by their column class
                # col-name = Player name
                # col-stat = Status  
                # col-desc = Description
                
                name_cell = row.find('td', class_='col-name')
                status_cell = row.find('td', class_='col-stat')
                desc_cell = row.find('td', class_='col-desc')
                
                if name_cell:
                    # Get player name from the anchor tag or direct text
                    player_link = name_cell.find('a', class_='AnchorLink')
                    player = player_link.get_text(strip=True) if player_link else name_cell.get_text(strip=True)
                    
                    status = status_cell.get_text(strip=True) if status_cell else 'Out'
                    description = desc_cell.get_text(strip=True) if desc_cell else ''
                    
                    if player:  # Only add if we got a player name
                        injuries.append({
                            'player': player,
                            'status': status,
                            'injury': description,
                            'source': 'ESPN'
                        })
            
            if injuries:
                injuries_by_team[team_abbr] = injuries
                print(f"  ✅ {team_abbr}: {len(injuries)} injuries")
            else:
                print(f"  ⚠️ {team_abbr}: No injuries found")
        
        print(f"\n✅ Total: Scraped injuries for {len(injuries_by_team)} teams")
        return injuries_by_team
        
    except Exception as e:
        print(f"❌ Error scraping ESPN: {e}")
        import traceback
        traceback.print_exc()
        return {}


def scrape_rotowire_injuries():
    """
    Backup scraper using RotoWire
    """
    try:
        url = "https://www.rotowire.com/basketball/nba-lineups.php"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        print(f"Fetching RotoWire: {url}...")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        injuries_by_team = {}
        
        # RotoWire shows lineups with injuries embedded
        lineup_cards = soup.find_all('div', class_='lineup')
        print(f"Found {len(lineup_cards)} lineup cards")
        
        for card in lineup_cards:
            # Get team abbreviation
            team_abbr_elem = card.find('div', class_='lineup__abbr')
            if not team_abbr_elem:
                continue
            
            team_abbr = team_abbr_elem.get_text(strip=True)
            
            # Find injury section
            injury_section = card.find('ul', class_='lineup__list--injuries')
            if not injury_section:
                continue
            
            injuries = []
            injury_items = injury_section.find_all('li')
            
            for item in injury_items:
                player_link = item.find('a')
                status_span = item.find('span', class_='lineup__inj')
                
                if player_link:
                    player_name = player_link.get_text(strip=True)
                    status = status_span.get_text(strip=True) if status_span else 'Out'
                    
                    injuries.append({
                        'player': player_name,
                        'status': status,
                        'injury': status,
                        'source': 'RotoWire'
                    })
            
            if injuries:
                injuries_by_team[team_abbr] = injuries
        
        print(f"✅ RotoWire: Found injuries for {len(injuries_by_team)} teams")
        return injuries_by_team
        
    except Exception as e:
        print(f"❌ Error scraping RotoWire: {e}")
        return {}


def map_team_name(team_name):
    """Map various team name formats to abbreviations"""
    team_name = team_name.lower().strip()
    
    # Remove common suffixes/prefixes
    team_name = re.sub(r'\s*injuries?\s*', '', team_name)
    team_name = re.sub(r'\s*injury report\s*', '', team_name)
    
    team_map = {
        'atlanta hawks': 'ATL', 'hawks': 'ATL', 'atl': 'ATL',
        'boston celtics': 'BOS', 'celtics': 'BOS', 'bos': 'BOS',
        'brooklyn nets': 'BKN', 'nets': 'BKN', 'bkn': 'BKN',
        'charlotte hornets': 'CHA', 'hornets': 'CHA', 'cha': 'CHA',
        'chicago bulls': 'CHI', 'bulls': 'CHI', 'chi': 'CHI',
        'cleveland cavaliers': 'CLE', 'cavaliers': 'CLE', 'cavs': 'CLE', 'cle': 'CLE',
        'dallas mavericks': 'DAL', 'mavericks': 'DAL', 'mavs': 'DAL', 'dal': 'DAL',
        'denver nuggets': 'DEN', 'nuggets': 'DEN', 'den': 'DEN',
        'detroit pistons': 'DET', 'pistons': 'DET', 'det': 'DET',
        'golden state warriors': 'GSW', 'warriors': 'GSW', 'gsw': 'GSW',
        'houston rockets': 'HOU', 'rockets': 'HOU', 'hou': 'HOU',
        'indiana pacers': 'IND', 'pacers': 'IND', 'ind': 'IND',
        'la clippers': 'LAC', 'los angeles clippers': 'LAC', 'clippers': 'LAC', 'lac': 'LAC',
        'la lakers': 'LAL', 'los angeles lakers': 'LAL', 'lakers': 'LAL', 'lal': 'LAL',
        'memphis grizzlies': 'MEM', 'grizzlies': 'MEM', 'mem': 'MEM',
        'miami heat': 'MIA', 'heat': 'MIA', 'mia': 'MIA',
        'milwaukee bucks': 'MIL', 'bucks': 'MIL', 'mil': 'MIL',
        'minnesota timberwolves': 'MIN', 'timberwolves': 'MIN', 'wolves': 'MIN', 'min': 'MIN',
        'new orleans pelicans': 'NOP', 'pelicans': 'NOP', 'nop': 'NOP',
        'new york knicks': 'NYK', 'knicks': 'NYK', 'nyk': 'NYK',
        'oklahoma city thunder': 'OKC', 'thunder': 'OKC', 'okc': 'OKC',
        'orlando magic': 'ORL', 'magic': 'ORL', 'orl': 'ORL',
        'philadelphia 76ers': 'PHI', '76ers': 'PHI', 'sixers': 'PHI', 'phi': 'PHI',
        'phoenix suns': 'PHX', 'suns': 'PHX', 'phx': 'PHX',
        'portland trail blazers': 'POR', 'trail blazers': 'POR', 'blazers': 'POR', 'por': 'POR',
        'sacramento kings': 'SAC', 'kings': 'SAC', 'sac': 'SAC',
        'san antonio spurs': 'SAS', 'spurs': 'SAS', 'sas': 'SAS',
        'toronto raptors': 'TOR', 'raptors': 'TOR', 'tor': 'TOR',
        'utah jazz': 'UTA', 'jazz': 'UTA', 'uta': 'UTA',
        'washington wizards': 'WAS', 'wizards': 'WAS', 'wiz': 'WAS', 'was': 'WAS',
    }
    
    return team_map.get(team_name)


def get_current_injuries():
    """Get current injuries with caching and multiple fallbacks"""
    global _injury_cache, _cache_timestamp
    
    # Return cache if valid
    if _cache_timestamp and datetime.now() - _cache_timestamp < CACHE_DURATION:
        print(f"Using cached injury data ({len(_injury_cache)} teams)")
        return _injury_cache
    
    # Try ESPN first (most reliable)
    print("\n=== Attempting ESPN scrape ===")
    injuries = scrape_espn_injuries()
    
    # If ESPN fails, try RotoWire
    if not injuries:
        print("\n=== ESPN failed, trying RotoWire ===")
        injuries = scrape_rotowire_injuries()
    
    # Update cache if we got data
    if injuries:
        _injury_cache = injuries
        _cache_timestamp = datetime.now()
        print(f"✅ Cached injury data for {len(injuries)} teams")
    else:
        print("⚠️ No injuries scraped, using old cache if available")
    
    return _injury_cache if _injury_cache else {}


def count_missing_starters(team_abbr, team_main_lineup):
    """
    Count how many starters from the main lineup are injured
    
    Args:
        team_abbr: Team abbreviation (e.g., 'LAL')
        team_main_lineup: List of main rotation player names
    
    Returns:
        int: Number of main players currently injured
    """
    injuries = get_current_injuries()
    team_injuries = injuries.get(team_abbr, [])
    
    if not team_injuries:
        return 0
    
    # Get list of injured player names (lowercase for matching)
    injured_players = [inj['player'].lower() for inj in team_injuries]
    
    # Count how many main lineup players are injured
    missing_count = 0
    
    for player_name in team_main_lineup:
        player_lower = player_name.lower()
        
        # Get last name for matching (more reliable)
        last_name = player_lower.split()[-1] if ' ' in player_lower else player_lower
        
        # Check if this player is in the injury list
        for injured in injured_players:
            if last_name in injured:
                missing_count += 1
                print(f"  Found injured starter: {player_name}")
                break
    
    return missing_count


def get_team_injury_summary(team_abbr):
    """Get a summary of a team's current injuries"""
    injuries = get_current_injuries()
    team_injuries = injuries.get(team_abbr, [])
    
    return {
        'team': team_abbr,
        'total_injuries': len(team_injuries),
        'injuries': team_injuries
    }


# Test function
if __name__ == "__main__":
    print("Testing ESPN Injury Scraper...")
    print("=" * 60)
    
    injuries = get_current_injuries()
    
    print(f"\n📊 Total teams with injuries: {len(injuries)}")
    
    if injuries:
        # Show teams with injuries
        teams_with_injuries = [(team, inj_list) for team, inj_list in injuries.items() if inj_list]
        print(f"Teams that have injuries: {len(teams_with_injuries)}")
        
        for team, team_injuries in teams_with_injuries[:5]:
            print(f"\n{team} ({len(team_injuries)} injuries):")
            for inj in team_injuries[:3]:  # Show first 3
                print(f"  • {inj['player']}: {inj['status']}")
                if inj['injury']:
                    print(f"    {inj['injury'][:80]}...")
    else:
        print("\n⚠️ No injuries found")
    
    print("\n" + "=" * 60)
    print("Test complete!")