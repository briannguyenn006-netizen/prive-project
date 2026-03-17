import feedparser
import os
import re
from datetime import datetime
from bs4 import BeautifulSoup
import google.generativeai as genai

# ==========================================
# 1. CẤU HÌNH AI
# ==========================================
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    print("⚠️ Lỗi: Không tìm thấy API Key!")
else:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

RSS_SOURCES = {
    'Global Desk': 'http://feeds.reuters.com/reuters/businessNews',
    'Market Intelligence': 'https://www.cnbc.com/id/10000667/device/rss/rss.html',
    'Institutional Report': 'https://feeds.a.dj.com/rss/WSJcomUSBusiness.xml'
}

def get_thumbnail(entry):
    # Cơ chế fix thumbnail lỗi: Ưu tiên lấy từ media, nếu không có lấy ảnh stock xịn
    img_url = ""
    if 'media_content' in entry: img_url = entry.media_content[0]['url']
    elif 'enclosures' in entry and len(entry.enclosures) > 0: img_url = entry.enclosures[0]['url']
    
    if not img_url:
        summary = entry.summary if 'summary' in entry else ""
        soup = BeautifulSoup(summary, 'html.parser')
        img = soup.find('img')
        if img: img_url = img['src']

    # Nếu vẫn không có ảnh, dùng ảnh stock tài chính sang trọng
    if not img_url or "doubleclick" in img_url:
        stock_images = [
            "https://images.unsplash.com/photo-1611974717482-58a252c85aec?auto=format&fit=crop&w=1200",
            "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?auto=format&fit=crop&w=1200"
        ]
        import random
        img_url = random.choice(stock_images)
    return img_url

def rewrite_with_ai(title, summary):
    prompt = f"""
    Act as a Senior Market Strategist at 'BrokeNoMore'. Rewrite this news into a detailed 250-word institutional report. 
    Focus on market impact, technical outlook, and strategic takeaways. 
    DO NOT mention any news agencies. Use a cold, professional, high-end tone.
    Title: {title}
    Data: {summary}
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip().replace('**', '')
    except:
        return f"Strategic analysis for {title} is currently being updated by the global desk."

def run_auto_news():
    posts_dir = 'posts'
    if not os.path.exists(posts_dir): os.makedirs(posts_dir)
    all_articles = []

    for provider, url in RSS_SOURCES.items():
        feed = feedparser.parse(url)
        for entry in feed.entries[:4]:
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
                    body {{ font-family: 'Inter', sans-serif; line-height: 1.8; color: #111; max-width: 800px; margin: 0 auto; padding: 60px 20px; }}
                    .logo {{ font-weight: 900; font-size: 24px; text-transform: uppercase; letter-spacing: -1px; margin-bottom: 50px; display: block; text-decoration: none; color: #000; }}
                    h1 {{ font-size: 42px; font-weight: 900; line-height: 1.1; margin-bottom: 30px; letter-spacing: -1.5px; }}
                    .meta {{ font-size: 13px; color: #666; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 40px; border-bottom: 1px solid #eee; padding-bottom: 20px; }}
                    img {{ width: 100%; border-radius: 4px; margin-bottom: 40px; }}
                    .content {{ font-size: 19px; white-space: pre-wrap; }}
                    .back {{ margin-top: 60px; display: inline-block; font-weight: 700; color: #000; text-decoration: none; border: 2px solid #000; padding: 10px 20px; }}
                </style></head>
                <body>
                    <a href="../index.html" class="logo">BrokeNoMore</a>
                    <h1>{entry.title}</h1>
                    <div class='meta'>{datetime.now().strftime('%B %d, %Y')} • Filed by BNM Intelligence</div>
                    <img src='{thumb}'>
                    <div class='content'>{ai_content}</div>
                    <a href='../index.html' class='back'>← BACK TO TERMINAL</a>
                </body></html>
                """)
            
            all_articles.append({'title': entry.title, 'provider': provider, 'thumb': thumb, 'path': filepath, 'summary': ai_content[:200]+"...", 'time': datetime.now().strftime('%H:%M')})

    # Render Index.html với Logo bên trái, không Chart
    hero = all_articles[0]
    side_news = "".join([f"<div class='side-item'><span class='time'>{a['time']}</span><a href='{a['path']}'>{a['title']}</a></div>" for a in all_articles[1:6]])
    grid_news = "".join([f"<div class='grid-item'><img src='{a['thumb']}'><div class='grid-content'><span class='meta'>{a['provider']}</span><a href='{a['path']}'>{a['title']}</a></div></div>" for a in all_articles[6:]])

    index_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Inter', sans-serif; margin: 0; background: #fff; color: #000; }}
            header {{ padding: 30px 5%; border-bottom: 1px solid #eee; display: flex; align-items: center; }}
            .logo {{ font-size: 32px; font-weight: 900; text-transform: uppercase; letter-spacing: -1.5px; text-decoration: none; color: #000; }}
            .ticker-wrap {{ background: #000; color: #fff; padding: 10px 0; }}
            .main-container {{ max-width: 1300px; margin: 40px auto; padding: 0 25px; display: grid; grid-template-columns: 2fr 1fr; gap: 60px; }}
            .hero-article img {{ width: 100%; height: 550px; object-fit: cover; border-radius: 4px; }}
            .hero-article h2 {{ font-size: 48px; font-weight: 900; line-height: 1.05; margin: 25px 0; letter-spacing: -2px; }}
            .hero-article h2 a {{ text-decoration: none; color: inherit; }}
            .side-news {{ border-left: 1px solid #eee; padding-left: 40px; }}
            .side-item {{ margin-bottom: 30px; padding-bottom: 20px; border-bottom: 1px solid #f5f5f5; }}
            .side-item .time {{ font-size: 11px; font-weight: 900; color: #cc0000; display: block; }}
            .side-item a {{ text-decoration: none; color: #000; font-weight: 700; font-size: 20px; line-height: 1.2; display: block; margin-top: 5px; }}
            .grid-section {{ grid-column: 1 / span 2; display: grid; grid-template-columns: repeat(4, 1fr); gap: 30px; border-top: 2px solid #000; padding-top: 40px; }}
            .grid-item img {{ width: 100%; height: 180px; object-fit: cover; border-radius: 3px; }}
            .grid-item a {{ text-decoration: none; color: #000; font-weight: 700; font-size: 16px; display: block; margin-top: 10px; }}
            @media (max-width: 900px) {{ .main-container {{ grid-template-columns: 1fr; }} .side-news {{ border-left: none; padding-left: 0; }} .grid-section {{ grid-template-columns: 1fr 1fr; }} }}
        </style>
    </head>
    <body>
        <header><a href="/" class="logo">BrokeNoMore</a></header>
        <div class="ticker-wrap">
            <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
            {{ "symbols": [{{"proName": "OANDA:XAUUSD", "title": "GOLD"}}, {{"proName": "BITSTAMP:BTCUSD", "title": "BTC"}}, {{"proName": "FX_IDC:USDVND", "title": "USDVND"}}], "colorTheme": "dark", "locale": "en" }}
            </script>
        </div>
        <div class="main-container">
            <div class="hero-article">
                <img src="{hero['thumb']}">
                <h2><a href="{hero['path']}">{hero['title']}</a></h2>
                <p style="font-size: 19px; line-height: 1.6; color: #333;">{hero['summary']}</p>
            </div>
            <div class="side-news">
                <h3 style="font-size: 13px; text-transform: uppercase; border-bottom: 2px solid #000; padding-bottom: 5px; margin-bottom: 25px;">Latest Intelligence</h3>
                {side_news_html}
            </div>
            <div class="grid-section">{grid_news_html}</div>
        </div>
    </body>
    </html>
    """
    with open('index.html', 'w', encoding='utf-8') as f: f.write(index_content)
    print("✅ Clean Terminal deployed successfully!")

if __name__ == "__main__":
    run_auto_news()
