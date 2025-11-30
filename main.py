import requests
import re
import os
from datetime import datetime

# 待抓取的网站列表 (基于您提供的Top 10)
URLS = [
    "https://www.freeclashnode.com/",
    "https://wanzhuanmi.com/",
    "https://oneclash.cc/",
    "https://clashnodes.com/",
    "https://clashnode.cc/",
    "https://www.mibei77.com/",
    "https://www.cfmem.com/",
    "https://www.85la.com/",
    "https://github.com/Pawdroid/Free-servers", # GitHub 项目可能需要特殊处理，这里尝试通用抓取
    "https://nodecats.com/"
]

# 模拟浏览器头，防止被简单拦截
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def fetch_and_extract():
    all_links = set()
    
    print(f"Starting scrape at {datetime.now()}...")
    
    for url in URLS:
        try:
            print(f"Visiting: {url}")
            response = requests.get(url, headers=HEADERS, timeout=15)
            response.encoding = 'utf-8' # 确保中文不乱码
            content = response.text
            
            # 正则匹配：查找 http/https 开头，并以 .yaml, .yml, .txt 结尾的链接
            # 也可以根据需要调整正则来匹配 vmess:// 等节点，但订阅链接更方便管理
            links = re.findall(r'https?://[^\s<>"]+?(?:\.yaml|\.yml|\.txt)', content)
            
            if links:
                print(f"  -> Found {len(links)} links.")
                for link in links:
                    # 简单的过滤：排除一些明显不是节点的链接（如 robots.txt 等）
                    if "robots.txt" not in link and "license" not in link.lower():
                        all_links.add(link)
            else:
                print("  -> No links found.")
                
        except Exception as e:
            print(f"  -> Error fetching {url}: {e}")

    # 将结果保存到文件
    save_to_file(all_links)

def save_to_file(links):
    filename = "nodes_list.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# Updated at: {datetime.now()}\n")
        f.write(f"# Total links: {len(links)}\n\n")
        for link in sorted(links):
            f.write(link + "\n")
    
    print(f"\nSuccessfully saved {len(links)} links to {filename}")

if __name__ == "__main__":
    fetch_and_extract()
