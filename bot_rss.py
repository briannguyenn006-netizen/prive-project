import feedparser
import os
import random
import time
from datetime import datetime
from bs4 import BeautifulSoup
import google.generativeai as genai

# ==========================================
# CẤU HÌNH AI & NGUỒN TIN
# ==========================================
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

RSS_SOURCES = {
    'Global': 'http://feeds.reuters.com/reuters/businessNews',
    'Markets': 'https://www.cnbc.com/id/10000667/device/rss/rss.html',
    'WSJ': 'https://feeds.a.dj.com/rss/WSJcomUSBusiness.xml'
}

def get_thumbnail(entry):
    # Dùng ảnh Stock xịn nếu nguồn tin chặn bot
    stock_imgs = [
        "https://images.unsplash.com/photo-1611974717482-58a252c85aec?w=800&q=80",
        "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=800&q=80",
        "https://images.unsplash.com/photo-1640343830005-ee0505d307bb?w=800&q=80",
        "https://images.unsplash.com/photo-1526303328184-c7e33f57f4c8?w=800&q=80"
    ]
    img = ""
    if 'media_content' in entry: img = entry.media_content[0]['url']
    elif 'enclosures' in entry and len(entry.enclosures) > 0: img = entry.enclosures[0]['url']
    
    if not img or any(x in img for x in ["doubleclick", "pixel", "feedburner"]):
        return random.choice(stock_imgs)
    return img

def rewrite_with_ai(title, summary):
    # Prompt "bạo lực" hơn để ép viết ít nhất 400 từ
    prompt = f"""
    Write a 400-word deep institutional market analysis for: {title}.
    Using this context: {summary}.
    
    STRUCTURE:
    1. MACRO ENVIRONMENT: Detailed breakdown (2 paragraphs).
    2. TECHNICAL IMPACT: Analysis of liquidity and volatility (2 paragraphs).
    3. BNM STRATEGY: Actionable advice for institutional investors (1 paragraph).
    
    Tone: Sophisticated, cold, Bloomberg-style. NO bold (**). NO source mentions. 
    IF YOU WRITE SHORT, YOU WILL FAIL.
    """
    try:
        # Ép AI viết đến khi đạt độ dài tối thiểu
        for _ in range(3):
            res = model.generate_content(prompt)
            content = res.text.strip().replace('**', '')
            if len(content) > 1000: return content # Trả về nếu đủ dài
        return content
    except:
        return "Analysis expansion in progress. Contact BNM Terminal for full data."

def run_auto_news():
    posts_dir = 'posts'
    if not os.path.exists(posts_dir): os.makedirs(posts_dir)
    all_articles = []
    v_id = int(time.time())

    # Lấy nhiều tin hơn để fill đầy layout
    for _, url in RSS_SOURCES.items():
        feed = feedparser.parse(url)
        for entry in feed.entries[:5]: # Lấy 5 tin mỗi nguồn = 15 tin tổng cộng
            thumb = get_thumbnail(entry)
            clean_summary = BeautifulSoup(entry.summary, 'html.parser').get_text()[:500]
            ai_content = rewrite_with_ai(entry.title, clean_summary)
            
            clean_title = "".join(x for x in entry.title if x.isalnum() or x==" ")
            filename = f"{datetime.now().strftime('%H%M%S')}-{clean_title[:15]}.html"
            filepath = os.path.join(posts_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"""
                <html><head><meta charset='UTF-8'><title>{entry.title} | BNM</title>
                <link rel="icon" type="image/png" href="../favicon.png?v={v_id}">
                <link href='https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap' rel='stylesheet'>
                <style>body{{font-family:'Inter';line-height:1.8;max-width:850px;margin:0 auto;padding:60px 20px;color:#111;background:#fff}}h1{{font-size:48px;letter-spacing:-3px;line-height:1;margin-bottom:30px}}img{{width:100%;margin:30px 0;border-radius:4px}}.content{{white-space:pre-wrap;font-size:20px;color:#222}}</style></head>
                <body><header style='border-bottom:2px solid #000;padding-bottom:20px'><a href='../index.html?v={v_id}' style='text-decoration:none;color:#000;font-weight:900;text-transform:uppercase'>BrokeNoMore</a></header>
                <h1>{entry.title}</h1><div style='color:#666;text-transform:uppercase;font-size:12px;margin-bottom:20px'>Institutional Report • {datetime.now().strftime('%d %b %Y')}</div><img src='{thumb}'><div class='content'>{ai_content}</div></body></html>
                """)
            all_articles.append({'title': entry.title, 'thumb': thumb, 'path': filepath, 'summary': ai_content[:200], 'time': datetime.now().strftime('%H:%M')})

    # Render Index.html - LAYOUT GRID SIÊU DÀY
    hero = all_articles[0]
    side_news = "".join([f"<div style='margin-bottom:20px;border-bottom:1px solid #eee;padding-bottom:15px;'><span style='color:red;font-size:10px;font-weight:900'>{a['time']}</span><br><a href='{a['path']}?v={v_id}' style='color:#000;text-decoration:none;font-weight:700;font-size:16px;line-height:1.2;display:block;margin-top:5px;'>{a['title']}</a></div>" for a in all_articles[1:8]])
    
    grid_html = ""
    for a in all_articles[8:]: # Tất cả những bài còn lại sẽ vào Grid
        grid_html += f"""
        <div style="margin-bottom:40px;">
            <img src="{a['thumb']}" style="width:100%;height:200px;object-fit:cover;border-radius:3px;">
            <h3 style="font-size:20px;margin:15px 0 10px;line-height:1.2;"><a href="{a['path']}?v={v_id}" style="color:#000;text-decoration:none;">{a['title']}</a></h3>
            <p style="font-size:14px;color:#444;line-height:1.5;">{a['summary']}...</p>
        </div>"""

    index_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8"><title>BrokeNoMore | Terminal</title>
        <link rel="icon" type="image/png" href="favicon.png?v={v_id}">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Inter', sans-serif; margin: 0; background: #fff; }}
            header {{ padding: 25px 5%; border-bottom: 5px solid #000; }}
            .logo {{ font-size: 42px; font-weight: 900; text-transform: uppercase; color: #000; text-decoration: none; letter-spacing: -3px; }}
            .main-grid {{ max-width: 1450px; margin: 40px auto; padding: 0 25px; display: grid; grid-template-columns: 2.5fr 1fr; gap: 60px; }}
            .news-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 40px; margin-top: 60px; border-top: 4px solid #000; padding-top: 40px; }}
            @media (max-width: 1000px) {{ .main-grid, .news-grid {{ grid-template-columns: 1fr; }} }}
        </style>
    </head>
    <body>
        <header><a href="/" class="logo">BrokeNoMore</a></header>
        <div style="background:#000; padding:12px 0;">
            <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
            {{ "symbols": [{{"proName": "OANDA:XAUUSD", "title": "GOLD"}}, {{"proName": "BITSTAMP:BTCUSD", "title": "BTC"}}, {{"proName": "FX_IDC:USDVND", "title": "USDVND"}}, {{"proName": "NASDAQ:TSLA", "title": "TSLA"}}], "colorTheme": "dark", "locale": "en" }}
            </script>
        </div>
        <div class="main-grid">
            <div>
                <img src="{hero['thumb']}" style="width:100%; height:550px; object-fit:cover; border-radius:4px;">
                <h2 style="font-size:52px; font-weight:900; letter-spacing:-3px; line-height:1; margin:30px 0;"><a href="{hero['path']}?v={v_id}" style="color:#000;text-decoration:none;">{hero['title']}</a></h2>
                <p style="font-size:22px; color:#333; line-height:1.7;">{hero['summary']}...</p>
                <div class="news-grid">{grid_html}</div>
            </div>
            <div style="border-left: 1px solid #eee; padding-left: 40px;">
                <h3 style="font-size:14px; text-transform:uppercase; border-bottom:4px solid #000; padding-bottom:8px; margin-bottom:30px; font-weight:900;">Latest Intelligence</h3>
                {side_news}
            </div>
        </div>
    </body>
    </html>
    """
    with open('index.html', 'w', encoding='utf-8') as f: f.write(index_content)

if __name__ == "__main__":
    run_auto_news()
