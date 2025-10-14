"""
Basketball Reference scraper using urllib (bypasses Cloudflare)
"""

from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
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


if __name__ == "__main__":
    import sys
    
    print("="*60)
    print("Basketball Reference Stats Scraper (urllib)")
    print("="*60)
    
    if len(sys.argv) > 1:
        player_name = sys.argv[1]
    else:
        player_name = "Lebron James"
    
    print(f"\nScraping stats for: {player_name}\n")
    
    stats = scrape_breference_stats(player_name)
    print(stats)