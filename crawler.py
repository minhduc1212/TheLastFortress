import requests
from bs4 import BeautifulSoup
import urllib.parse
import json
import time

def scrape_fmhy_exact_content(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"Error accessing {url}. Status code: {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')
        content_container = soup.select_one('.vp-doc') 
        
        if not content_container:
            return None

        data = {
            "url": url,
            "title": soup.title.get_text(strip=True) if soup.title else "No Title",
            "sections": []
        }

        current_section = None

        for element in content_container.find_all(['h2', 'h3', 'p', 'ul']):
            if element.name in ['h2', 'h3']:
                if current_section:
                    data["sections"].append(current_section)
                
                heading_text = element.get_text(strip=True).replace('#', '').replace('​', '').strip()
                current_section = {
                    "heading": heading_text,
                    "level": element.name,
                    "text_explanations": [],
                    "resource_items": []
                }
                
            elif current_section:
                if element.name == 'p':
                    text = element.get_text(strip=True)
                    if text and "Got feedback?" not in text:
                        current_section["text_explanations"].append(text)
                        
                elif element.name == 'ul':
                    for li_tag in element.find_all('li'):
                        full_text = li_tag.get_text(separator=" ", strip=True)
                        
                        links_in_li = []
                        for a_tag in li_tag.find_all('a', href=True):
                            link_url = a_tag['href']
                            if not link_url.startswith('#'):
                                if link_url.startswith('/'):
                                    link_url = f"https://fmhy.net{link_url}"
                                    
                                links_in_li.append({
                                    "name": a_tag.get_text(strip=True),
                                    "url": link_url
                                })
                        
                        if links_in_li:
                            current_section["resource_items"].append({
                                "full_text": full_text, 
                                "links": links_in_li
                            })
                        elif full_text:
                            current_section["text_explanations"].append(full_text)

        if current_section:
            data["sections"].append(current_section)

        return data
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def run_scrapper():
    print("Starting crawler...")
    base_url = "https://fmhy.net"
    target_url = f"{base_url}/beginners-guide"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(target_url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            sidebar = soup.find('aside') 

            if sidebar:
                links = sidebar.find_all('a')
                print(f"Found {len(links)} links. Starting crawl...\n")
                
                all_crawled_data = []
                for item in links:
                    name = item.get_text(strip=True)
                    href = item.get('href')
                    
                    if name and href:
                        full_link = urllib.parse.urljoin(base_url, href)
                        print(f"Crawling: {name}")
                        
                        scraped_data = scrape_fmhy_exact_content(full_link)
                        if scraped_data:
                            all_crawled_data.append({
                                "category_name": name,
                                "content": scraped_data
                            })
                        time.sleep(1) # Be nice to the server
                        
                with open('fmhy_all_data.json', 'w', encoding='utf-8') as f:
                    json.dump(all_crawled_data, f, ensure_ascii=False, indent=4)
                    
                print(f"Success! Saved {len(all_crawled_data)} categories to fmhy_all_data.json.")
            else:
                print("Could not find sidebar.")
        else:
            print(f"Failed to load target URL: {response.status_code}")
    except Exception as e:
        print(f"Crawl failed: {e}")

if __name__ == "__main__":
    run_scrapper()
