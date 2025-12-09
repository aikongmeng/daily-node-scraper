import requests
import re
import time
from urllib.parse import urljoin, urlparse
from datetime import datetime

# ----------------配置区域----------------
# 待抓取的网站列表
URLS = [
    "https://www.freeclashnode.com/",
    "https://yoyapai.com/mianfeijiedian",
    "https://wanzhuanmi.com/",
    "https://oneclash.cc/",
    "https://clashnodes.com/",
    "https://clashnode.cc/",
    "https://www.mibei77.com/",
    "https://www.cfmem.com/",
    "https://www.85la.com/",
    "https://nodecats.com/",
    "https://github.com/Pawdroid/Free-servers" # GitHub 这种页面可能直接有链接，也可能需要深挖
]

# 模拟浏览器请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# 每个网站最多深入访问多少个子页面（防止超时）
MAX_DEPTH_PAGES = 15 

# ----------------核心代码----------------

def get_html(url):
    """发送请求获取网页源码"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.encoding = 'utf-8' # 强制UTF-8，防止中文乱码
        return response.text
    except Exception as e:
        print(f"    [Error] Failed to fetch {url}: {e}")
        return None

def extract_subs(content):
    """从文本内容中正则匹配 .yaml 或 .txt 的 http 链接"""
    if not content:
        return []
    # 正则说明：匹配 http/s 开头，不包含引号/空格/尖括号，以 .yaml/.yml/.txt 结尾
    pattern = r'https?://[^\s<>"\'\(\)]+?(?:\.yaml|\.yml|\.txt)'
    links = re.findall(pattern, content)
    return links

def extract_internal_links(base_url, html):
    """提取首页中的内部链接（可能是文章详情页）"""
    if not html:
        return []
    
    # 提取所有 href
    raw_links = re.findall(r'href=["\'](.*?)["\']', html)
    
    valid_links = []
    domain = urlparse(base_url).netloc
    
    for link in raw_links:
        # 补全相对路径
        full_link = urljoin(base_url, link)
        parsed = urlparse(full_link)
        
        # 过滤逻辑：
        # 1. 必须是同域名
        # 2. 排除 .css, .js, .png 等非页面资源
        # 3. 排除 /tag/, /category/ 等分类页，尽量只抓文章页
        # 4. 排除 #锚点
        if parsed.netloc == domain and "#" not in full_link:
            if not re.search(r'\.(css|js|png|jpg|jpeg|gif|ico|xml|json)$', parsed.path, re.I):
                # 简单的去重列表
                if full_link not in valid_links and full_link != base_url:
                     # 针对博客类网站，通常文章链接比较长，或者包含数字/日期
                     # 这里做一个简单的长度判断，过滤掉 overly short links (like /, /about)
                     if len(parsed.path) > 4: 
                        valid_links.append(full_link)
    
    return valid_links

def main():
    all_subs = set()
    
    print(f"🚀 Task started at {datetime.now()}\n")

    for site_url in URLS:
        print(f"🌐 Scanning Site: {site_url}")
        
        # 1. 访问首页
        home_html = get_html(site_url)
        if not home_html:
            continue
            
        # 2. 尝试直接在首页找订阅链接
        home_subs = extract_subs(home_html)
        if home_subs:
            print(f"    [Success] Found {len(home_subs)} subs on Homepage.")
            for sub in home_subs:
                all_subs.add(sub)
        
        # 3. 挖掘二级页面 (Deep Dive)
        # 提取首页的所有链接，选取前 MAX_DEPTH_PAGES 个进行访问
        internal_links = extract_internal_links(site_url, home_html)
        
        # 只要前几个，因为通常最新的节点文章在最上面
        target_links = internal_links[:MAX_DEPTH_PAGES]
        
        if target_links:
            print(f"    [Deep Dive] Visiting top {len(target_links)} sub-pages...")
            
            for sub_page_url in target_links:
                # 延时一下，对服务器友好
                time.sleep(1) 
                sub_html = get_html(sub_page_url)
                deep_subs = extract_subs(sub_html)
                
                if deep_subs:
                    print(f"      -> Found {len(deep_subs)} subs in {sub_page_url}")
                    for sub in deep_subs:
                        all_subs.add(sub)
        else:
             print("    [Info] No relevant sub-pages found.")

        print("-" * 30)

    # 4. 保存结果
    save_to_file(all_subs)

def save_to_file(links):
    filename = "nodes_list.txt"
    # 过滤一些垃圾链接（如包含 localhost, example 等）
    valid_links = [l for l in links if "localhost" not in l and "127.0.0.1" not in l]
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# Auto-scraped Node Subscriptions\n")
        f.write(f"# Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"# Total found: {len(valid_links)}\n\n")
        for link in sorted(valid_links):
            f.write(link + "\n")
    
    print(f"\n✅ Done! Saved {len(valid_links)} unique links to {filename}")

if __name__ == "__main__":
    main()
