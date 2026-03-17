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

# Nguồn tin (Xóa dấu vết nguồn)
RSS_SOURCES = {
    'Global Desk': 'http://feeds.reuters.com/reuters/businessNews',
    'Market Intelligence': 'https://www.cnbc.com/id/10000667/device/rss/rss.html',
    'Institutional Desk': 'https://feeds.a.dj.com/rss/WSJcomUSBusiness.xml'
}

# 1. FIX LỖI ẢNH: Cơ chế fallback sang trọng
def get_thumbnail(entry):
    img_url = ""
    if 'media_content' in entry: img_url = entry.media_content[0]['url']
    elif 'enclosures' in entry and len(entry.enclosures) > 0: img_url = entry.enclosures[0]['url']
    
    # List ảnh stock tài chính cực đẹp (Unsplash)
    fallback_images = [
        "https://images.unsplash.com/photo-1611974717482-58a252c85aec?q=80&w=1200&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?q=80&w=1200&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1640343830005-ee0505d307bb?q=80&w=1200&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1633156191771-700947264a2c?q=80&w=1200&auto=format&fit=crop"
    ]
    
    # Kiểm tra link rác hoặc trống
    if not img_url or "doubleclick" in img_url or "feeds.feedburner.com" in img_url:
        return random.choice(fallback_images)
    return img_url

# 2. FIX TIN NGẮN: Prompt mới siêu sâu sắc
def rewrite_with_ai(title, summary):
    prompt = f"""
    Act as the Lead Market Strategist at BrokeNoMore. 
    Rewrite this news into a detailed, professional institutional report (minimum 300 words).
    
    Structure:
    - Paragraph 1: Detailed Overview of the situation.
    - Paragraph 2: Strategic Analysis of market implications (liquidity, sectors, sentiment).
    - Paragraph 3: The BrokeNoMore outlook and technical perspective.
    
    Tone: Sophisticated, data-driven, cold. NO source citations. NO boldformatting.
    Title: {title}. Raw Data: {summary}
    """
    try:
        response = model.generate_content(prompt)
        # Fix lỗi bold trầy trật lúc nãy
        return response.text.strip().replace('**', '') 
    except:
        return f"Market analysis for {title} is currently being processed by our global intelligence desk."

def run_auto_news():
    posts_dir = 'posts'
    if not os.path.exists(posts_dir): os.makedirs(posts_dir)
    all_articles = []
    
    # ID version để chống cache trình duyệt lỳ lợm
    v_id = int(time.time())

    for provider, url in RSS_SOURCES.items():
        feed = feedparser.parse(url)
        for entry in feed.entries[:3]: # Lấy 3 tin chất lượng nhất
            thumb = get_thumbnail(entry)
            clean_summary = BeautifulSoup(entry.summary, 'html.parser').get_text()
            ai_content = rewrite_with_ai(entry.title, clean_summary)
            
            clean_title = "".join(x for x in entry.title if x.isalnum() or x==" ")
            filename = f"{datetime.now().strftime('%H%M%S')}-{clean_title[:20]}.html"
            filepath = os.path.join(posts_dir, filename)
            
            # 3. FIX CHI TIẾT BÀI VIẾT: Giao diện Bloomberg cao cấp
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"""
                <html><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'>
                <link rel="icon" type="image/png" href="../favicon.png?v={v_id}">
                <link href='https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,700&family=Inter:wght@400;500;700&display=swap' rel='stylesheet'>
                <style>
                    body {{ font-family: 'Inter', sans-serif; line-height: 1.8; color: #1a1a1a; max-width: 850px; margin: 0 auto; padding: 60px 20px; background: #fff; }}
                    .kicker {{ color: #cc0000; font-weight: 800; text-transform: uppercase; font-size: 13px; letter-spacing: 1.5px; margin-bottom: 15px; display: block; }}
                    h1 {{ font-family: 'Playfair Display', serif; font-size: 48px; line-height: 1.1; margin-bottom: 25px; letter-spacing: -1px; }}
                    .meta {{ color: #888; font-size: 14px; border-top: 1px solid #eee; padding-top: 20px; margin-bottom: 40px; font-style: italic; }}
                    img {{ width: 100%; height: auto; margin-bottom: 40px; box-shadow: 0 15px 45px rgba(0,0,0,0.08); }}
                    .content {{ font-size: 20px; color: #222; white-space: pre-wrap; }}
                    .back {{ margin-top: 60px; display: inline-block; text-decoration: none; color: #000; font-weight: 700; font-size: 13px; text-transform: uppercase; border: 2px solid #000; padding: 12px 25px; }}
                </style></head>
                <body>
                    <span class='kicker'>BrokeNoMore Intelligence Desk</span>
                    <h1>{entry.title}</h1>
                    <div class='meta'>Reported on {datetime.now().strftime('%B %d, %Y')} • BNM Global Desk</div>
                    <img src='{thumb}'>
                    <div class='content'>{ai_content}</div>
                    <a href='../index.html?v={v_id}' class='back'>← BACK TO TERMINAL</a>
                </body></html>
                """)
            
            all_articles.append({'title': entry.title, 'provider': provider, 'thumb': thumb, 'path': filepath, 'summary': ai_content[:300]+"...", 'time': datetime.now().strftime('%H:%M')})

    # Render TRANG CHỦ (Fix Favicon, Fix Layout)
    hero = all_articles[0]
    side_html = "".join([f"<div style='margin-bottom:20px;'><span style='font-size:11px; color:#cc0000; font-weight:900;'>{a['time']}</span><br><a href='{a['path']}?v={v_id}' style='text-decoration:none; color:#000; font-weight:700; font-size:17px; line-height:1.3;'>{a['title']}</a></div>" for a in all_articles[1:6]])
    grid_html = "".join([f"<div style='margin-bottom:30px;'><img src='{a['thumb']}' style='width:100%; height:160px; object-fit:cover; border-radius:2px;'><br><a href='{a['path']}?v={v_id}' style='text-decoration:none; color:#000; font-weight:700; display:block; margin-top:10px;'>{a['title']}</a></div>" for a in grid_news])

    index_content = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="icon" type="image/png" href="favicon.png?v={v_id}">
        <title>BrokeNoMore | Global Market Terminal</title>
        <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
        <style>
            :root {{ --bg: #ffffff; --text: #121212; --accent: #cc0000; --border: #e5e5e5; }}
            body {{ font-family: 'Inter', sans-serif; margin: 0; background: var(--bg); color: var(--text); }}
            header {{ border-bottom: 5px solid var(--text); padding: 25px 0; margin: 0 5%; text-align: center; }}
            .logo {{ font-family: 'Playfair Display', serif; font-size: 52px; font-weight: 900; letter-spacing: -2px; color: var(--text); text-decoration: none; }}
            .main-container {{ max-width: 1300px; margin: 40px auto; padding: 0 25px; display: grid; grid-template-columns: 2.2fr 1fr; gap: 40px; }}
            .hero-article img {{ width: 100%; height: 500px; object-fit: cover; border-radius: 4px; }}
            .hero-article h2 {{ font-family: 'Playfair Display', serif; font-size: 42px; margin: 20px 0 10px; line-height: 1.1; }}
            .side-news {{ border-left: 1px solid var(--border); padding-left: 40px; }}
            .section-title {{ font-size: 13px; font-weight: 800; text-transform: uppercase; border-bottom: 3px solid var(--text); padding-bottom: 5px; margin-bottom: 25px; display: block; }}
            .grid-item img {{ width: 100%; height: 160px; object-fit: cover; }}
            @media (max-width: 950px) {{ .main-container {{ grid-template-columns: 1fr; }} .side-news {{ border-left: none; padding-left: 0; }} }}
        </style>
    </head>
    <body>
        <header><a href="/" class="logo">BrokeNoMore</a></header>
        <div style="background: #000; color: #fff; padding: 10px 0;">
            <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
            {{ "symbols": [{{"proName": "OANDA:XAUUSD", "title": "GOLD"}}, {{"proName": "BITSTAMP:BTCUSD", "title": "BTC"}}, {{"proName": "FX_IDC:USDVND", "title": "USDVND"}}], "colorTheme": "dark", "locale": "vi_VN" }}
            </script>
        </div>
        <div class="main-container">
            <div>
                <img src="{hero['thumb']}" class="hero-img">
                <h2><a href="{hero['path']}?v={v_id}" style="text-decoration:none; color:#000;">{hero['title']}</a></h2>
                <p style="font-size:18px; color:#333; line-height:1.6; margin-bottom:40px;">{hero['summary']}</p>
                <div style="display:grid; grid-template-columns: repeat(2, 1fr); gap:30px; border-top:2px solid #000; padding-top:30px;">{grid_html}</div>
            </div>
            <div class="side-news">
                <span class="section-title">Latest Intelligence</span>
                {side_html}
            </div>
        </div>
        <footer style="margin-top: 80px; padding: 60px 0; text-align: center; font-size: 13px; color: #888; border-top: 1px solid #eee; background: #f9f9f9;">
            <p>&copy; 2026 BrokeNoMore Terminal • Private & Proprietary</p>
        </footer>
    </body>
    </html>
    """
    with open('index.html', 'w', encoding='utf-8') as f: f.write(index_content)
    print("✅ Full Reconstruction Complete! Favicon Fixed. Short News Fixed. Image Falling Fixed.")
