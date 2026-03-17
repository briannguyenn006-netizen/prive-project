import feedparser
import os
import re
import random
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
    'Institutional Report': 'https://feeds.a.dj.com/rss/WSJcomUSBusiness.xml'
}

def get_thumbnail(entry):
    # Fix triệt để thumbnail trắng
    img_url = ""
    if 'media_content' in entry: img_url = entry.media_content[0]['url']
    elif 'enclosures' in entry and len(entry.enclosures) > 0: img_url = entry.enclosures[0]['url']
    
    # Danh sách ảnh Stock tài chính cực xịn (Unsplash) để fallback
    stock_images = [
        "https://images.unsplash.com/photo-1611974717482-58a252c85aec?auto=format&fit=crop&w=1200",
        "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?auto=format&fit=crop&w=1200",
        "https://images.unsplash.com/photo-1640343830005-ee0505d307bb?auto=format&fit=crop&w=1200"
    ]
    
    # Kiểm tra xem link ảnh có "sạch" không, nếu không thì lấy stock
    if not img_url or "doubleclick" in img_url or "feeds.feedburner.com" in img_url:
        return random.choice(stock_images)
    return img_url

def rewrite_with_ai(title, summary):
    prompt = f"Act as a Senior Strategist at BrokeNoMore. Rewrite this in 250 words with institutional depth, market impact analysis, and a professional tone. No citations of sources. Title: {title}. Data: {summary}"
    try:
        response = model.generate_content(prompt)
        return response.text.strip().replace('**', '')
    except:
        return f"Market analysis for {title} is currently being finalized by our BNM Intelligence desk."

def run_auto_news():
    posts_dir = 'posts'
    if not os.path.exists(posts_dir): os.makedirs(posts_dir)
    all_articles = []

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
                    body {{ font-family: 'Inter', sans-serif; line-height: 1.8; color: #111; max-width: 800px; margin: 0 auto; padding: 40px 20px; }}
                    header {{ margin-bottom: 40px; border-bottom: 1px solid #eee; padding-bottom: 20px; }}
                    .logo {{ font-weight: 900; font-size: 20px; text-transform: uppercase; text-decoration: none; color: #000; }}
                    h1 {{ font-size: 40px; font-weight: 900; line-height: 1.1; margin: 30px 0; letter-spacing: -1.5px; }}
                    .meta {{ font-size: 13px; color: #666; text-transform: uppercase; margin-bottom: 30px; }}
                    img {{ width: 100%; border-radius: 4px; margin-bottom: 30px; }}
                    .content {{ font-size: 19px; }}
                    .back {{ margin-top: 50px; display: inline-block; font-weight: 700; color: #000; text-decoration: none; border-bottom: 2px solid #000; }}
                </style></head>
                <body>
                    <header><a href="../index.html" class="logo">BrokeNoMore</a></header>
                    <h1>{entry.title}</h1>
                    <div class='meta'>{datetime.now().strftime('%d %b %Y')} • Filed by BNM Intelligence Desk</div>
                    <img src='{thumb}'>
                    <div class='content'>{ai_content}</div>
                    <a href='../index.html' class='back'>← BACK TO TERMINAL</a>
                </body></html>
                """)
            all_articles.append({'title': entry.title, 'provider': provider, 'thumb': thumb, 'path': filepath, 'summary': ai_content[:180]+"...", 'time': datetime.now().strftime('%H:%M')})

    # Render Index.html (Logo Trái - Không Chart)
    hero = all_articles[0]
    side_html = "".join([f"<div style='margin-bottom:20px;'><span style='font-size:11px; color:red; font-weight:900;'>{a['time']}</span><br><a href='{a['path']}' style='text-decoration:none; color:#000; font-weight:700; font-size:17px;'>{a['title']}</a></div>" for a in all_articles[1:6]])
    grid_html = "".join([f"<div style='margin-bottom:30px;'><img src='{a['thumb']}' style='width:100%; height:150px; object-fit:cover;'><br><a href='{a['path']}' style='text-decoration:none; color:#000; font-weight:700; display:block; margin-top:10px;'>{a['title']}</a></div>" for a in all_articles[6:]])

    index_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Inter', sans-serif; margin: 0; background: #fff; }}
            header {{ padding: 25px 5%; display: flex; align-items: center; border-bottom: 1px solid #eee; }}
            .logo {{ font-size: 28px; font-weight: 900; text-transform: uppercase; text-decoration: none; color: #000; letter-spacing: -1.5px; }}
            .main-container {{ max-width: 1300px; margin: 40px auto; padding: 0 20px; display: grid; grid-template-columns: 2.2fr 1fr; gap: 50px; }}
            .hero-img {{ width: 100%; height: 500px; object-fit: cover; border-radius: 4px; }}
            .hero-title {{ font-size: 44px; font-weight: 900; line-height: 1.1; margin: 20px 0; letter-spacing: -2px; }}
            @media (max-width: 900px) {{ .main-container {{ grid-template-columns: 1fr; }} }}
        </style>
    </head>
    <body>
        <header><a href="/" class="logo">BrokeNoMore</a></header>
        <div class="main-container">
            <div>
                <img src="{hero['thumb']}" class="hero-img">
                <h2 class="hero-title"><a href="{hero['path']}" style="text-decoration:none; color:#000;">{hero['title']}</a></h2>
                <p style="font-size:18px; color:#333; line-height:1.6;">{hero['summary']}</p>
                <div style="margin-top:50px; display:grid; grid-template-columns: 1fr 1fr; gap:30px; border-top:2px solid #000; padding-top:30px;">{grid_html}</div>
            </div>
            <div style="border-left: 1px solid #eee; padding-left: 30px;">
                <h3 style="font-size:12px; text-transform:uppercase; border-bottom:2px solid #000; padding-bottom:5px; margin-bottom:20px;">Intelligence Feed</h3>
                {side_html}
            </div>
        </div>
    </body>
    </html>
    """
    with open('index.html', 'w', encoding='utf-8') as f: f.write(index_content)
