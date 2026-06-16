import os
import re
import time
import json
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://everythingmoe.com/",
    "Cookie": "nsfw=true"
}

BASE_URL = "https://everythingmoe.com"

# Local caching configuration
CACHE_DIR = ".everythingmoe_cache"
EXPAND_CACHE_DIR = os.path.join(CACHE_DIR, "expand_cache")
os.makedirs(EXPAND_CACHE_DIR, exist_ok=True)

def fetch_url(url, retries=3, delay=1):
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
            if response.status_code == 200:
                return response
            elif response.status_code == 404:
                return response
            elif response.status_code == 429:
                print(f"Rate limited (429) fetching {url}. Retrying in {delay * 2}s...")
                time.sleep(delay * 2)
                delay *= 2
            else:
                print(f"Error {response.status_code} fetching {url}. Retrying...")
                time.sleep(delay)
                delay *= 1.5
        except Exception as e:
            print(f"Exception fetching {url}: {e}. Retrying...")
            time.sleep(delay)
            delay *= 1.5
    return None

def parse_details(details_dict):
    if not details_dict:
        return {}
    res = {}
    for k, v in details_dict.items():
        if not isinstance(v, str):
            res[k] = v
            continue
            
        if k in ('positive', 'negative'):
            res[k + 's'] = [x.strip() for x in v.split('#') if x.strip()]
        elif k in ('altlink', 'ex-altlink', 'exx-altlink'):
            links = []
            for item in v.split('#'):
                if not item.strip():
                    continue
                if '<<' in item:
                    parts = item.split('<<', 1)
                    name = parts[0].strip()
                    url = parts[1].strip()
                    if url.startswith('/'):
                        url = BASE_URL + url
                    links.append({'name': name, 'url': url})
                else:
                    url = item.strip()
                    if url.startswith('/'):
                        url = BASE_URL + url
                    links.append({'name': '', 'url': url})
            res[k + 's'] = links
        else:
            res[k] = v
    return res

def parse_html_page(html_content, is_graveyard=False):
    soup = BeautifulSoup(html_content, 'html.parser')
    sections_list = []
    
    # Find all divs with class "section"
    for sec_div in soup.find_all(class_='section'):
        sec_id = sec_div.get('id', '')
        if not sec_id.startswith('sec-') or sec_id == 'sec-bookmark':
            continue
        
        section_name = sec_id.replace('sec-', '')
        
        # Title
        title_span = sec_div.find(class_='title-text')
        if not title_span:
            continue
        
        title_text = ''
        for child in title_span.children:
            if getattr(child, 'name', None) != 'div': # Skip count or other div tags
                title_text += str(child)
        title_text = BeautifulSoup(title_text, 'html.parser').get_text().strip()
        # Clean trailing parenthesized numbers (e.g. "Anime Streaming (83)" -> "Anime Streaming")
        title_text = re.sub(r'\s*\(\d+\)\s*$', '', title_text)
        
        # Notes
        notes_div = sec_div.find(class_='section-notes')
        notes = notes_div.get_text(strip=True) if notes_div else ''
        
        sites = []
        # Find all section-items
        for item_div in sec_div.find_all(class_='section-item'):
            # Skip expand button
            classes = item_div.get('class', [])
            if 'section-expandbtn' in classes or 'section-morebtn' in classes:
                continue
                
            # Parse rank
            rank = item_div.get('data-rank', '')
            
            # Parse filter/tags
            filter_attr = item_div.get('data-filter', '')
            tags = [t.strip() for t in filter_attr.split(',') if t.strip()] if filter_attr else []
            
            # Find the link tag
            a_tag = item_div.find('a')
            if not a_tag:
                continue
                
            title = a_tag.get_text(strip=True)
            href = a_tag.get('href', '')
            external_link = a_tag.get('data-link', '')
            
            # Icon
            img_tag = a_tag.find('img')
            icon_url = img_tag.get('src', '') if img_tag else ''
            
            # Status flags
            is_licensed = 'section-licensed' in classes
            is_nsfw = 'nsfwsection' in classes
            
            # Also extract tags inside the item div (like NSFW tags or other spans)
            for span in item_div.find_all('span', class_='nsfwtag'):
                is_nsfw = True
            for span in item_div.find_all('span', class_='addtag'):
                t_text = span.get_text(strip=True)
                if t_text not in tags:
                    tags.append(t_text)
            
            # Site ID
            site_id = href[3:] if href.startswith('/s/') else href
            
            # Determine if it has details (presence of morebtn class in div)
            has_details = (item_div.find(class_='morebtn') is not None)
            
            site_obj = {
                'id': site_id,
                'title': title,
                'link': external_link,
                'icon': icon_url,
                'tags': tags,
                'rank': int(rank) if rank.isdigit() else rank,
                'is_licensed': is_licensed,
                'is_nsfw': is_nsfw,
                'has_details': has_details,
                'status': 'graveyard' if is_graveyard else 'active',
                'section': section_name
            }
            sites.append(site_obj)
            
        # Check for lowcont container
        lowcont_div = sec_div.find(class_='lowcont')
        lowcont_id = lowcont_div.get('id', '') if lowcont_div else ''
        
        sections_list.append({
            'name': section_name,
            'title': title_text,
            'notes': notes,
            'is_graveyard': is_graveyard,
            'lowcont_id': lowcont_id,
            'sites': sites
        })
        
    return sections_list

def main():
    # 1. Fetch main.json cached data
    main_cache_path = os.path.join(CACHE_DIR, "main_cache.json")
    print("Fetching main cache JSON...")
    r = fetch_url(f"{BASE_URL}/data/cache/main.json")
    if r and r.status_code == 200:
        main_cache = r.json()
        with open(main_cache_path, "w", encoding="utf-8") as f:
            json.dump(main_cache, f, indent=2, ensure_ascii=False)
        print("Successfully updated main_cache.json.")
    else:
        print("Failed to fetch fresh main cache. Loading local main_cache.json...")
        if os.path.exists(main_cache_path):
            with open(main_cache_path, "r", encoding="utf-8") as f:
                main_cache = json.load(f)
        else:
            print("No main_cache.json available! Starting with empty cache.")
            main_cache = {}

    # 2. Fetch index.html
    index_path = os.path.join(CACHE_DIR, "index.html")
    print("Fetching index page (with NSFW)...")
    r = fetch_url(f"{BASE_URL}/")
    if r and r.status_code == 200:
        index_html = r.text
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(index_html)
        print("Successfully updated index.html.")
    else:
        print("Failed to fetch index page. Loading local index.html...")
        with open(index_path, "r", encoding="utf-8") as f:
            index_html = f.read()

    # 3. Fetch graveyard.html
    graveyard_path = os.path.join(CACHE_DIR, "graveyard.html")
    print("Fetching graveyard page (with NSFW)...")
    r = fetch_url(f"{BASE_URL}/graveyard")
    if r and r.status_code == 200:
        graveyard_html = r.text
        with open(graveyard_path, "w", encoding="utf-8") as f:
            f.write(graveyard_html)
        print("Successfully updated graveyard.html.")
    else:
        print("Failed to fetch graveyard page. Loading local graveyard.html...")
        with open(graveyard_path, "r", encoding="utf-8") as f:
            graveyard_html = f.read()

    # 4. Parse pages
    print("Parsing HTML pages...")
    active_sections = parse_html_page(index_html, is_graveyard=False)
    graveyard_sections = parse_html_page(graveyard_html, is_graveyard=True)

    # 5. Fetch lowsec JSONs
    for section in active_sections + graveyard_sections:
        if section['lowcont_id']:
            suffix = section['lowcont_id'].replace('lowcont-', '')
            lowsec_url = f"{BASE_URL}/data/lowsec/{suffix}.json"
            print(f"Fetching lowsec data for section '{section['name']}' ({suffix})...")
            
            # Rate limiting delay
            time.sleep(0.2)
            res = fetch_url(lowsec_url)
            if res and res.status_code == 200:
                lowsec_data = res.json()
                start_rank = len(section['sites']) + 1
                for idx, item in enumerate(lowsec_data):
                    site_id = item.get('id')
                    has_details = True
                    if not site_id:
                        site_id = item.get('tempid', '')
                        has_details = False
                        
                    # Parse filters/tags
                    filter_str = item.get('filter', '')
                    tags = [t.strip() for t in filter_str.split(',') if t.strip()] if filter_str else []
                    
                    ex_tags_str = item.get('tags', '')
                    ex_tags = [t.strip() for t in ex_tags_str.split(' ') if t.strip()] if ex_tags_str else []
                    for t in ex_tags:
                        if t not in tags:
                            tags.append(t)
                            
                    is_licensed = 'licensed' in tags or 'licensed' in ex_tags
                    is_nsfw = 'nsfw' in tags or 'nsfw' in ex_tags
                    
                    site_obj = {
                        'id': site_id,
                        'title': item.get('title', ''),
                        'link': item.get('link', ''),
                        'icon': item.get('icon', ''),
                        'tags': tags,
                        'rank': start_rank + idx,
                        'is_licensed': is_licensed,
                        'is_nsfw': is_nsfw,
                        'has_details': has_details,
                        'status': 'graveyard' if section['is_graveyard'] else 'active',
                        'section': section['name']
                    }
                    section['sites'].append(site_obj)
                print(f"Added {len(lowsec_data)} low-rank sites to section '{section['name']}'.")
            else:
                print(f"Failed to fetch lowsec data for section '{section['name']}'.")

    # 6. Fetch details for every site that has them
    print("Collecting and structuring site details...")
    all_sites = {}
    
    # First, list all sites and find which ones need details fetched from the server
    sites_to_fetch_details = []
    
    for section in active_sections + graveyard_sections:
        for site in section['sites']:
            site_id = site['id']
            if not site_id:
                continue
                
            # If we've already processed this site, update its sections list
            if site_id in all_sites:
                if section['name'] not in all_sites[site_id]['sections']:
                    all_sites[site_id]['sections'].append(section['name'])
                continue
                
            # Structuring the flat site object
            site_entry = {
                'id': site_id,
                'title': site['title'],
                'link': site['link'],
                'icon': site['icon'],
                'tags': site['tags'],
                'is_licensed': site['is_licensed'],
                'is_nsfw': site['is_nsfw'],
                'status': site['status'],
                'sections': [section['name']],
                'details': {}
            }
            all_sites[site_id] = site_entry
            
            if site['has_details']:
                # If it's in the main cache, load it immediately
                if site_id in main_cache:
                    site_entry['details'] = parse_details(main_cache[site_id])
                else:
                    # We need to fetch it from the server
                    sites_to_fetch_details.append(site_id)
            
    # Fetch details for sites not in main_cache (mostly graveyard sites)
    total_to_fetch = len(sites_to_fetch_details)
    print(f"Need to fetch detailed info for {total_to_fetch} sites (not in main cache)...")
    
    for idx, site_id in enumerate(sites_to_fetch_details, 1):
        local_detail_path = os.path.join(EXPAND_CACHE_DIR, f"{site_id}.json")
        details = None
        
        # Check local cache first
        if os.path.exists(local_detail_path):
            try:
                with open(local_detail_path, "r", encoding="utf-8") as f:
                    details = json.load(f)
            except Exception:
                pass
                
        if details is None:
            print(f"[{idx}/{total_to_fetch}] Fetching details for '{site_id}' from server...")
            time.sleep(0.25) # Throttle to prevent 429
            detail_url = f"{BASE_URL}/data/expand/{site_id}.json"
            res = fetch_url(detail_url)
            if res and res.status_code == 200:
                details = res.json()
                # Save to local cache
                with open(local_detail_path, "w", encoding="utf-8") as f:
                    json.dump(details, f, indent=2, ensure_ascii=False)
            elif res and res.status_code == 404:
                details = {}
                with open(local_detail_path, "w", encoding="utf-8") as f:
                    json.dump(details, f, indent=2, ensure_ascii=False)
            else:
                print(f"Failed to fetch details for '{site_id}'.")
                details = {}
                
        all_sites[site_id]['details'] = parse_details(details)

    # 7. Merge details back to the sections site list for consistency
    for section in active_sections + graveyard_sections:
        for site in section['sites']:
            site_id = site['id']
            if site_id in all_sites:
                site['details'] = all_sites[site_id]['details']

    # 8. Save the final JSON dataset directly in root workspace
    final_dataset = {
        "active_sections": active_sections,
        "graveyard_sections": graveyard_sections,
        "all_sites": all_sites
    }
    
    output_path = "everythingmoe_data.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_dataset, f, indent=2, ensure_ascii=False)
        
    alternative_output_path = "everythingmoe.json"
    with open(alternative_output_path, "w", encoding="utf-8") as f:
        json.dump(final_dataset, f, indent=2, ensure_ascii=False)
        
    print(f"\nCrawling completed successfully!")
    print(f"Total sections: {len(active_sections) + len(graveyard_sections)}")
    print(f"Total unique sites: {len(all_sites)}")
    print(f"Saved dataset to: {output_path}")
    print(f"Saved dataset copy to: {alternative_output_path}")

if __name__ == "__main__":
    main()