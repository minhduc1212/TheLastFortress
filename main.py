import requests
from bs4 import BeautifulSoup
import urllib.parse

# Cấu hình URL mục tiêu
base_url = "https://fmhy.net"
target_url = f"{base_url}/beginners-guide"

# Gửi yêu cầu HTTP GET đến trang web
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
response = requests.get(target_url, headers=headers)

# Kiểm tra nếu truy cập thành công
if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    
    sidebar = soup.find('aside') 

    if sidebar:
        links = sidebar.find_all('a')
        print(f"Tìm thấy {len(links)} mục trong thanh bar bên trái:\n")
        print("=" * 40)
        
        for item in links:
            name = item.get_text(strip=True) # Lấy tên hiển thị và loại bỏ khoảng trắng thừa
            href = item.get('href')          # Lấy đường dẫn (link)
            
            if name and href:
                full_link = urllib.parse.urljoin(base_url, href)
                
                print(f"Tên mục : {name}")
                print(f"Link    : {full_link}")
                print("-" * 40)
    else:
        print("Không tìm thấy phần tử đại diện cho thanh bar bên trái.")
        print("Hãy nhấn F12 (Inspect) trên trình duyệt để kiểm tra xem thanh bên trái dùng thẻ/class HTML nào và cập nhật lại biến 'sidebar'.")
else:
    print(f"Không thể truy cập trang web. Mã lỗi: {response.status_code}")