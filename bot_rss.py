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
    model = genai.GenerativeModel('gemini-1.5-flash')

RSS_SOURCES = {
    'Global Desk': 'http://feeds.reuters.com/reuters/businessNews',
    'Market Intelligence': 'https://www.cnbc.com/id/10000667/device/rss/rss.html',
    'Institutional Desk': 'https://feeds.a.dj.com/rss/WSJcomUSBusiness.xml'
}

def get_thumbnail(entry):
    img_url = ""
    if 'media_content' in entry: img_url = entry.media_content[0]['url']
    elif 'enclosures' in entry and len(entry.enclosures) > 0: img_url = entry.enclosures[0]['url']
    
    # List ảnh Stock cực xịn để không bao giờ bị lỗi ảnh trắng
    fallback_images = [
        "https://images.unsplash.com/photo-1611974717482-58a252c85aec?auto=format&fit=crop&w=1200",
        "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?auto=format&fit=crop&w=1200",
        "https://images.unsplash.com/photo-1640343830005-ee0505d307bb?auto=format&fit=crop&w=1200"
    ]
    if not img_url or any(x in img_url for x in ["doubleclick", "pixel", "feedburner"]):
        return random.choice(fallback_images)
    return img_url

def rewrite_with_ai(title, summary):
    # Prompt "bạo lực" hơn để ép AI viết dài 400 từ
    prompt = f"""
    Act as a Senior Market Strategist at BrokeNoMore. 
    Rewrite this news into a deep institutional report (minimum 400 words).
    
    STRUCTURE:
    1. MARKET DYNAMICS: Detailed overview.
    2. RISK ASSESSMENT: Macro and technical analysis.
    3. STRATEGIC OUTLOOK: Specific investor guidance.
    
    RULES: No bold (**). No mentions of Reuters/CNBC. Cold, professional tone. 
    Each section must be at least 2 long paragraphs.
    Title: {title}. News: {summary}
    """
    try:
        response = model.generate_content(prompt)
        text = response.text.strip().replace('**', '')
        return text if len(text) > 500 else f"Analysis for {title} is being expanded by our desk..."
    except:
        return f"Strategic analysis for {title} is currently pending."

def run_auto_news():
    posts_dir = 'posts'
    if not os.path.exists(posts_dir): os.makedirs(posts_dir)
    all_articles = []
    v_id = int(time.time())

    for provider, url in RSS_SOURCES.items():
        feed = feedparser.parse(url)
        for entry in feed.entries[:3]:
            thumb = get_thumbnail(entry)
            clean_summary = BeautifulSoup(entry.summary, 'html.parser').get_text() if 'summary' in entry else "Pending data"
            ai_content = rewrite_with_ai(entry.title, clean_summary)
            
            clean_title = "".join(x for x in entry.title if x.isalnum() or x==" ")
            filename = f"{datetime.now().strftime('%H%M%S')}-{clean_title[:20]}.html"
            filepath = os.path.join(posts_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"""
                <html><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'>
                <title>{entry.title} | BrokeNoMore</title>
                <link rel="icon" type="image/png" href="../favicon.png?v={v_id}">
                <link href='https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap' rel='stylesheet'>
                <style>
                    body {{ font-family: 'Inter', sans-serif; line-height: 1.8; color: #111; max-width: 800px; margin: 0 auto; padding: 40px 20px; }}
                    header {{ margin-bottom: 40px; border-bottom: 2px solid #000; padding-bottom: 20px; }}
                    .logo {{ font-weight: 900; font-size: 24px; text-transform: uppercase; text-decoration: none; color: #000; }}
                    h1 {{ font-size: 40px; font-weight: 900; line-height: 1.1; margin: 30px 0; letter-spacing: -2px; }}
                    img {{ width: 100%; border-radius: 4px; margin-bottom: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
                    .content {{ font-size: 19px; white-space: pre-wrap; }}
                    .back {{ margin-top: 50px; display: inline-block; font-weight: 700; color: #000; text-decoration: none; border: 2px solid #000; padding: 10px 20px; }}
                </style></head>
                <body>
                    <header><a href="../index.html?v={v_id}" class="logo">BrokeNoMore</a></header>
                    <h1>{entry.title}</h1>
                    <div style='color:#888; font-size:13px; margin-bottom:30px;'>{datetime.now().strftime('%B %d, %Y')} • BNM INTELLIGENCE</div>
                    <img src='{thumb}'>
                    <div class='content'>{ai_content}</div>
                    <a href='../index.html?v={v_id}' class='back'>← BACK TO TERMINAL</a>
                </body></html>
                """)
            all_articles.append({'title': entry.title, 'thumb': thumb, 'path': filepath, 'summary': ai_content[:280]+"...", 'time': datetime.now().strftime('%H:%M')})

    # Render Index.html (SỬA LỖI BIẾN GRID_NEWS)
    hero = all_articles[0]
    side_html = "".join([f"<div style='margin-bottom:20px; border-bottom:1px solid #eee; padding-bottom:15px;'><span style='font-size:11px; color:red; font-weight:900;'>{a['time']}</span><br><a href='{a['path']}?v={v_id}' style='text-decoration:none; color:#000; font-weight:700; font-size:17px; display:block; margin-top:5px;'>{a['title']}</a></div>" for a in all_articles[1:6]])
    grid_html = "".join([f"<div style='margin-bottom:30px;'><img src='{a['thumb']}' style='width:100%; height:160px; object-fit:cover; border-radius:4px;'><br><a href='{a['path']}?v={v_id}' style='text-decoration:none; color:#000; font-weight:700; display:block; margin-top:10px;'>{a['title']}</a></div>" for a in all_articles[6:]])

    index_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>BrokeNoMore | Terminal</title>
        <link rel="icon" type="image/png" href="favicon.png?v={v_id}">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Inter', sans-serif; margin: 0; background: #fff; }}
            header {{ padding: 30px 5%; border-bottom: 5px solid #000; display: flex; align-items: center; }}
            .logo {{ font-size: 32px; font-weight: 900; text-transform: uppercase; text-decoration: none; color: #000; letter-spacing: -2px; }}
            .main-container {{ max-width: 1400px; margin: 40px auto; padding: 0 20px; display: grid; grid-template-columns: 2.3fr 1fr; gap: 50px; }}
            .hero-img {{ width: 100%; height: 500px; object-fit: cover; border-radius: 4px; }}
            .hero-title {{ font-size: 48px; font-weight: 900; line-height: 1; margin: 25px 0; letter-spacing: -2.5px; }}
            @media (max-width: 900px) {{ .main-container {{ grid-template-columns: 1fr; }} }}
        </style>
    </head>
    <body>
        <header><a href="/" class="logo">BrokeNoMore</a></header>
        <div style="background:#000; padding:10px 0;">
            <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
            {{ "symbols": [{{"proName": "OANDA:XAUUSD", "title": "GOLD"}}, {{"proName": "BITSTAMP:BTCUSD", "title": "BTC"}}, {{"proName": "FX_IDC:USDVND", "title": "USDVND"}}], "colorTheme": "dark", "locale": "en" }}
            </script>
        </div>
        <div class="main-container">
            <div>
                <img src="{hero['thumb']}" class="hero-img">
                <h2 class="hero-title"><a href="{hero['path']}?v={v_id}" style="text-decoration:none; color:#000;">{hero['title']}</a></h2>
                <p style="font-size:20px; color:#333; line-height:1.7;">{hero['summary']}</p>
                <div style="margin-top:50px; display:grid; grid-template-columns: 1fr 1fr; gap:40px; border-top:3px solid #000; padding-top:40px;">{grid_html}</div>
            </div>
            <div style="border-left: 1px solid #eee; padding-left: 30px;">
                <h3 style="font-size:14px; text-transform:uppercase; border-bottom:3px solid #000; padding-bottom:5px; margin-bottom:25px; font-weight:900;">Latest</h3>
                {side_html}
            </div>
        </div>
    </body>
    </html>
    """
    with open('index.html', 'w', encoding='utf-8') as f: f.write(index_content)

if __name__ == "__main__":
    run_auto_news()
