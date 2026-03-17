import feedparser
import os
import re
import random
import time
from datetime import datetime
from bs4 import BeautifulSoup
import google.generativeai as genai

# ==========================================
# CẤU HÌNH AI
# ==========================================
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    # Dùng gemini-1.5-flash cho tốc độ, nhưng prompt ép viết dài
    model = genai.GenerativeModel('gemini-1.5-flash')

RSS_SOURCES = {
    'Global Desk': 'http://feeds.reuters.com/reuters/businessNews',
    'Market Intelligence': 'https://www.cnbc.com/id/10000667/device/rss/rss.html',
    'Institutional Report': 'https://feeds.a.dj.com/rss/WSJcomUSBusiness.xml'
}

def get_thumbnail(entry):
    img_url = ""
    if 'media_content' in entry: img_url = entry.media_content[0]['url']
    elif 'enclosures' in entry and len(entry.enclosures) > 0: img_url = entry.enclosures[0]['url']
    
    stock_images = [
        "https://images.unsplash.com/photo-1611974717482-58a252c85aec?auto=format&fit=crop&w=1200",
        "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?auto=format&fit=crop&w=1200",
        "https://images.unsplash.com/photo-1640343830005-ee0505d307bb?auto=format&fit=crop&w=1200",
        "https://images.unsplash.com/photo-1633156191771-700947264a2c?auto=format&fit=crop&w=1200"
    ]
    
    if not img_url or "doubleclick" in img_url or "feeds.feedburner.com" in img_url:
        return random.choice(stock_images)
    return img_url

def rewrite_with_ai(title, summary):
    # Prompt mới: Ép AI viết dài, có cấu trúc phân tích chuyên sâu
    prompt = f"""
    Act as a Lead Market Strategist at 'BrokeNoMore Intelligence'. 
    Your task is to rewrite this news into a deep, professional institutional report (minimum 250-300 words).
    
    Structure the response as follows:
    1. MARKET OVERVIEW: Detailed context of the event.
    2. STRATEGIC ANALYSIS: How this impacts global liquidity, specific sectors, and investor sentiment.
    3. THE BNM OUTLOOK: A forward-looking technical or fundamental conclusion.
    
    RULES: 
    - Use a cold, authoritative, and sophisticated tone.
    - NEVER mention original news agencies like Reuters or CNBC. 
    - Focus on macroeconomic implications.
    - No bold formatting inside the text.
    
    News Title: {title}
    Raw Data: {summary}
    """
    try:
        response = model.generate_content(prompt)
        content = response.text.strip().replace('**', '')
        return content
    except:
        return f"The strategic analysis for {title} is currently being finalized by our global research desk. Check back for the full institutional report."

def run_auto_news():
    posts_dir = 'posts'
    if not os.path.exists(posts_dir): os.makedirs(posts_dir)
    all_articles = []
    
    # Version ID để chống cache trình duyệt
    v_id = int(time.time())

    for provider, url in RSS_SOURCES.items():
        feed = feedparser.parse(url)
        for entry in feed.entries[:3]:
            thumb = get_thumbnail(entry)
            clean_summary = BeautifulSoup(entry.summary, 'html.parser').get_text()
            ai_content = rewrite_with_ai(entry.title, clean_summary)
            
            clean_title = "".join(x for x in entry.title if x.isalnum() or x==" ")
            filename = f"{datetime.now().strftime('%H%M%S')}-{clean_title[:20]}.html"
            filepath = os.path.join(posts_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"""
                <html><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'>
                <link href='https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap' rel='stylesheet'>
                <style>
                    body {{ font-family: 'Inter', sans-serif; line-height: 1.8; color: #111; max-width: 850px; margin: 0 auto; padding: 60px 20px; background: #fff; }}
                    header {{ margin-bottom: 50px; border-bottom: 2px solid #000; padding-bottom: 20px; }}
                    .logo {{ font-weight: 900; font-size: 24px; text-transform: uppercase; text-decoration: none; color: #000; }}
                    h1 {{ font-size: 44px; font-weight: 900; line-height: 1.1; margin: 30px 0; letter-spacing: -2px; color: #000; }}
                    .meta {{ font-size: 13px; color: #666; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 40px; }}
                    img {{ width: 100%; border-radius: 4px; margin-bottom: 40px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); }}
                    .content {{ font-size: 20px; color: #222; white-space: pre-wrap; }}
                    .back {{ margin-top: 60px; display: inline-block; font-weight: 900; color: #000; text-decoration: none; border-bottom: 3px solid #000; padding-bottom: 5px; text-transform: uppercase; }}
                </style></head>
                <body>
                    <header><a href="../index.html?v={v_id}" class="logo">BrokeNoMore</a></header>
                    <h1>{entry.title}</h1>
                    <div class='meta'>{datetime.now().strftime('%d %B %Y')} • Filed by BrokeNoMore Research Intelligence</div>
                    <img src='{thumb}'>
                    <div class='content'>{ai_content}</div>
                    <a href='../index.html?v={v_id}' class='back'>← Return to Market Terminal</a>
                </body></html>
                """)
            all_articles.append({'title': entry.title, 'provider': provider, 'thumb': thumb, 'path': filepath, 'summary': ai_content[:280]+"...", 'time': datetime.now().strftime('%H:%M')})

    # Render Index.html
    hero = all_articles[0]
    side_html = "".join([f"<div style='margin-bottom:25px; border-bottom:1px solid #eee; padding-bottom:15px;'><span style='font-size:11px; color:#cc0000; font-weight:900;'>{a['time']}</span><br><a href='{a['path']}?v={v_id}' style='text-decoration:none; color:#000; font-weight:700; font-size:18px; line-height:1.2; display:block; margin-top:5px;'>{a['title']}</a></div>" for a in all_articles[1:6]])
    grid_html = "".join([f"<div style='margin-bottom:40px;'><img src='{a['thumb']}' style='width:100%; height:180px; object-fit:cover; border-radius:3px;'><span style='font-size:11px; font-weight:900; color:#666; text-transform:uppercase; display:block; margin-top:15px;'>{a['provider']}</span><a href='{a['path']}?v={v_id}' style='text-decoration:none; color:#000; font-weight:700; font-size:18px; display:block; margin-top:8px; line-height:1.3;'>{a['title']}</a></div>" for a in all_articles[6:]])

    index_content = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Inter', sans-serif; margin: 0; background: #fff; color: #000; }}
            header {{ padding: 30px 5%; display: flex; align-items: center; border-bottom: 4px solid #000; }}
            .logo {{ font-size: 36px; font-weight: 900; text-transform: uppercase; text-decoration: none; color: #000; letter-spacing: -2px; }}
            .ticker-wrap {{ background: #000; color: #fff; padding: 12px 0; }}
            .main-container {{ max-width: 1400px; margin: 40px auto; padding: 0 30px; display: grid; grid-template-columns: 2.3fr 1fr; gap: 60px; }}
            .hero-img {{ width: 100%; height: 550px; object-fit: cover; border-radius: 4px; }}
            .hero-title {{ font-size: 52px; font-weight: 900; line-height: 1; margin: 30px 0 20px; letter-spacing: -3px; }}
            .side-news {{ border-left: 1px solid #eee; padding-left: 40px; }}
            .grid-section {{ grid-column: 1 / span 2; display: grid; grid-template-columns: repeat(4, 1fr); gap: 40px; border-top: 4px solid #000; padding-top: 50px; }}
            @media (max-width: 1000px) {{ .main-container {{ grid-template-columns: 1fr; }} .side-news {{ border-left: none; padding-left: 0; }} .grid-section {{ grid-template-columns: 1fr 1fr; }} }}
        </style>
    </head>
    <body>
        <header><a href="/" class="logo">BrokeNoMore</a></header>
        <div class="ticker-wrap">
            <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
            {{ "symbols": [
                {{"proName": "OANDA:XAUUSD", "title": "GOLD"}},
                {{"proName": "BITSTAMP:BTCUSD", "title": "BITCOIN"}},
                {{"proName": "FX_IDC:USDVND", "title": "USD/VND"}},
                {{"proName": "FOREXCOM:SPX3500", "title": "S&P 500"}},
                {{"proName": "NASDAQ:NDX", "title": "NASDAQ 100"}}
            ], "colorTheme": "dark", "isTransparent": false, "displayMode": "adaptive", "locale": "en" }}
            </script>
        </div>
        <div class="main-container">
            <div>
                <img src="{hero['thumb']}" class="hero-img">
                <h2 class="hero-title"><a href="{hero['path']}?v={v_id}" style="text-decoration:none; color:#000;">{hero['title']}</a></h2>
                <p style="font-size:20px; color:#333; line-height:1.7; margin-bottom:40px;">{hero['summary']}</p>
                <div class="grid-section">{grid_html}</div>
            </div>
            <div class="side-news">
                <h3 style="font-size:14px; text-transform:uppercase; border-bottom:3px solid #000; padding-bottom:8px; margin-bottom:30px; font-weight:900;">Intelligence Feed</h3>
                {side_html}
            </div>
        </div>
        <footer style="padding: 80px 0; text-align: center; border-top: 1px solid #eee; margin-top: 100px; font-size: 13px; color: #999;">
            <p>&copy; 2026 BrokeNoMore Intelligence Terminal • Private & Proprietary</p>
        </footer>
    </body>
    </html>
    """
    with open('index.html', 'w', encoding='utf-8') as f: f.write(index_content)
    print("✅ Terminal updated with deep analysis and anti-cache measures.")

if __name__ == "__main__":
    run_auto_news()
