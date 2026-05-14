import requests
from bs4 import BeautifulSoup
import json

def scrape_fmhy_exact_content(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Lỗi truy cập. Status code: {response.status_code}")
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
                "resource_items": [] # Đổi tên thành items để chứa cả text mô tả + links
            }
            
        elif current_section:
            if element.name == 'p':
                text = element.get_text(strip=True)
                if text and "Got feedback?" not in text:
                    current_section["text_explanations"].append(text)
                    
            elif element.name == 'ul':
                # FIX: Duyệt qua từng dòng <li> thay vì chỉ tìm thẻ <a>
                for li_tag in element.find_all('li'):
                    # Lấy TOÀN BỘ text của dòng (Bao gồm cả tên link + chữ mô tả đằng sau)
                    # separator=" " giúp các thẻ bên trong có khoảng cách hợp lý
                    full_text = li_tag.get_text(separator=" ", strip=True)
                    
                    # Tìm tất cả các link có trong dòng này
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
                    
                    # Nếu dòng <li> có chứa link, lưu lại cả dòng text và danh sách link
                    if links_in_li:
                        current_section["resource_items"].append({
                            "full_text": full_text, 
                            "links": links_in_li
                        })
                    # Nếu dòng <li> chỉ là bullet point text bình thường (không có link)
                    elif full_text:
                        current_section["text_explanations"].append(full_text)

    if current_section:
        data["sections"].append(current_section)

    return data

if __name__ == "__main__":
    target_url = "https://fmhy.net/beginners-guide"
    scraped_data = scrape_fmhy_exact_content(target_url)
    
    if scraped_data:
        with open('fmhy_exact_data.json', 'w', encoding='utf-8') as f:
            json.dump(scraped_data, f, ensure_ascii=False, indent=4)
        print("Đã quét thành công và giữ lại toàn bộ chữ mô tả!")