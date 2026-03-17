import feedparser, os, random, time, google.generativeai as genai
from datetime import datetime
from bs4 import BeautifulSoup

# ==========================================
# BNM TERMINAL - CORE CONFIG
# ==========================================
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

# Nguồn tin ổn định
RSS_SOURCES = {
    'Markets': 'https://www.cnbc.com/id/10000667/device/rss/rss.html',
    'Finance': 'https://www.cnbc.com/id/100003114/device/rss/rss.html',
    'Tech': 'https://www.cnbc.com/id/19854910/device/rss/rss.html'
}

def get_unique_img(title):
    # Lấy 2 từ đầu tiên để tạo query, đảm bảo mỗi tin có ảnh khác nhau
    words = [w for w in title.split() if len(w) > 3]
    query = "+".join(words[:2]) if words else "finance"
    # Dùng seed ngẫu nhiên để Unsplash trả về ảnh khác nhau
    seed = random.randint(1, 1000)
    return f"https://source.unsplash.com/featured/800x500?{query}&sig={seed}"

def analyze_and_force_length(title, summary):
    if not GOOGLE_API_KEY: return summary
    
    # PROMPT SIÊU GẮT - ÉP VIẾT DÀI (Hơn 1500 ký tự)
    prompt = f"""
    ACT AS A SENIOR WALL STREET ANALYST AT BROKENOMORE.
    Write a 500-word JAW-DROPPING financial deep-dive for: {title}.
    Using this context: {summary}.
    
    REQUIRED STRUCTURE:
    1. MARKET IMPLICATIONS & SENTIMENT (Must be 150+ words)
    2. FUNDAMENTAL DATA ANALYSIS (Must be 150+ words)
    3. INSTITUTIONAL INVESTOR VERDICT (Must be 100+ words)
    4. BNM STRATEGIC OUTLOOK (Must be 100+ words)
    
    STRICT RULES:
    - Sophisticated, aggressive language. English only. 
    - Strictly NO bold (**) symbols. NO bullet points. NO "Pending".
    - DO NOT BE BRIEF. IF YOU WRITE SHORT, YOU FAIL.
    """
    
    for _ in range(3): # Cho phép AI Retry đến 3 lần để đạt độ dài
        try:
            res = model.generate_content(prompt)
            content = res.text.replace('**', '').strip()
            # Kiểm tra độ dài: Nếu <1200 ký tự, AI phải viết lại
            if len(content) > 1200:
                return content
            time.sleep(1) # Tránh bị Gemini khóa do spam request
        except:
            continue
    # Nếu AI vẫn lười, lấy summary gốc cộng thêm câu lệnh cứu bồ
    return f"{summary}\n\n[BNM Intelligence Note: The terminal is manually expanding this high-density data stream due to market volatility. Full report pending.]"

def run_terminal():
    posts_dir = 'posts'
    # Dọn dẹp posts cũ để tránh lẫn favicon lỗi
    if not os.path.exists(posts_dir): os.makedirs(posts_dir)
    articles = []
    v = int(time.time())

    # Lấy tổng cộng 12 tin chất lượng
    for _, url in RSS_SOURCES.items():
        feed = feedparser.parse(url)
        for entry in feed.entries[:4]: 
            img = get_unique_img(entry.title)
            desc = BeautifulSoup(entry.summary, 'html.parser').get_text()
            # AI thực hiện phân tích
            content = analyze_and_force_length(entry.title, desc)
            
            # Tạo tên file
            fname = f"{datetime.now().strftime('%H%M%S')}-{random.randint(10,99)}.html"
            path = os.path.join(posts_dir, fname)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(f"""
                <html><head><meta charset='UTF-8'><title>{entry.title} | BNM</title>
                <link rel="icon" type="image/png" href="../favicon.png?v={v}">
                <link href='https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap' rel='stylesheet'>
                <style>body{{font-family:'Inter';max-width:800px;margin:0 auto;padding:60px 20px;line-height:2;color:#111;background:#fff}}
                a.back{{font-weight:900;text-decoration:none;color:#000;text-transform:uppercase}}
                h1{{font-size:45px;font-weight:900;letter-spacing:-3px;line-height:1}}img{{width:100%;border-radius:4px;margin:30px 0;box-shadow: 0 10px 30px rgba(0,0,0,0.1)}}p{{font-size:19px;text-align:justify}}</style></head>
                <body><a href='../index.html?v={v}' class='back'>← TERMINAL</a><h1>{entry.title}</h1><img src='{img}'><div style='white-space:pre-wrap'>{content}</div></body></html>
                """)
            articles.append({'t': entry.title, 'p': path, 's': content[:250], 'img': img, 'time': datetime.now().strftime('%H:%M')})

    # Render Index.html (Giao diện Grid)
    if not articles: return
    hero = articles[0]
    side_html = "".join([f"<div style='margin-bottom:20px;border-bottom:1px solid #eee;padding-bottom:15px;'><span style='color:red;font-size:10px;font-weight:900;'>{a['time']}</span><br><a href='{a['p']}?v={v}' style='color:#000;text-decoration:none;font-weight:700'>{a['t']}</a></div>" for a in articles[1:8]])
    grid_html = "".join([f"<div style='margin-bottom:40px;'><img src='{a['img']}' style='width:100%;height:220px;object-fit:cover;border-radius:4px;'><h3 style='font-size:20px;margin:15px 0 10px;font-weight:900;'><a href='{a['p']}?v={v}' style='color:#000;text-decoration:none;'>{a['t']}</a></h3><p style='font-size:14px;color:#555;'>{a['s']}...</p></div>" for a in articles[8:]])

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(f"""
        <!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>BNM Terminal</title>
        <link rel="icon" type="image/png" href="favicon.png?v={v}">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap" rel="stylesheet">
        <style>body{{font-family:'Inter';margin:0;background:#fff}}header{{padding:25px 5%;border-bottom:8px solid #000}}.logo{{font-size:40px;font-weight:900;text-transform:uppercase;color:#000;text-decoration:none;letter-spacing:-3px}}.container{{max-width:1400px;margin:40px auto;padding:0 20px;display:grid;grid-template-columns:2.5fr 1fr;gap:50px}}.grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:40px;margin-top:50px;border-top:5px solid #000;padding-top:40px}}@media(max-width:1000px){{.container,.grid{{grid-template-columns:1fr}}}}</style></head>
        <body><header><a href="/" class="logo">BrokeNoMore</a></header>
        <div style='background:#000;padding:10px 0'><script type='text/javascript' src='https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js' async>{{ "symbols": [{{"proName": "OANDA:XAUUSD", "title": "GOLD"}}, {{"proName": "BITSTAMP:BTCUSD", "title": "BTC"}}]}}</script></div>
        <div class="container"><div><img src='{hero['img']}' style='width:100%;height:550px;object-fit:cover;'><h1 style='font-size:55px;font-weight:900;letter-spacing:-3px;margin:25px 0;line-height:1'><a href='{hero['p']}?v={v}' style='color:#000;text-decoration:none;'>{hero['t']}</a></h1><p style='font-size:22px;color:#333'>{hero['s']}...</p><div class='grid'>{grid_html}</div></div>
        <div style='border-left:2px solid #000;padding-left:40px'><h3 style='font-size:12px;text-transform:uppercase;border-bottom:6px solid #000;padding-bottom:10px;margin-bottom:30px;font-weight:900'>Latest Intel</h3>{side_html}</div></div></body></html>
        """)

if __name__ == "__main__":
    run_terminal()
