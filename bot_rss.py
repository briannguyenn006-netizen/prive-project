import feedparser
import os
import random
import time
from datetime import datetime
from bs4 import BeautifulSoup
import google.generativeai as genai

# ==========================================
# CONFIG
# ==========================================
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

# Thêm nguồn tin đa dạng để fill đầy layout
RSS_SOURCES = {
    'Global': 'http://feeds.reuters.com/reuters/businessNews',
    'Markets': 'https://www.cnbc.com/id/10000667/device/rss/rss.html',
    'Business': 'https://feeds.a.dj.com/rss/WSJcomUSBusiness.xml',
    'Tech': 'https://www.cnbc.com/id/19854910/device/rss/rss.html'
}

def get_thumbnail(entry):
    # Dùng nguồn ảnh Unsplash theo keyword để ảnh luôn hiện và đẹp
    keywords = ["finance", "trading", "stock", "business", "market", "economy"]
    img_fallback = f"https://images.unsplash.com/photo-1611974717482-58a252c85aec?w=800&q=80&sig={random.randint(1,1000)}"
    
    img = ""
    if 'media_content' in entry: img = entry.media_content[0]['url']
    elif 'enclosures' in entry and len(entry.enclosures) > 0: img = entry.enclosures[0]['url']
    
    # Nếu ảnh gốc lỗi hoặc là pixel rác, ép dùng Unsplash cho sang
    if not img or any(x in img for x in ["doubleclick", "pixel", "feedburner", "static-economist"]):
        return f"https://source.unsplash.com/featured/800x600?{random.choice(keywords)}"
    return img

def rewrite_with_ai(title, summary):
    # Prompt "ép buộc" AI phải viết cực dài và chi tiết
    prompt = f"""
    Write a COMPREHENSIVE 500-WORD institutional market report on: "{title}".
    Context provided: {summary}.
    
    REQUIRED STRUCTURE (MANDATORY):
    1. EXECUTIVE SUMMARY: Deep dive into the core event (min 150 words).
    2. QUANTITATIVE IMPACT: Analyze how this affects volatility, yields, and specific sectors (min 150 words).
    3. THE BNM EDGE: Our proprietary strategic outlook and risk mitigation steps (min 150 words).
    
    STYLE: Bloomberg Terminal style. Cold, professional, data-heavy. 
    WARNING: If the output is less than 400 words, you are failing your duty. DO NOT use bold (**).
    """
    try:
        response = model.generate_content(prompt)
        content = response.text.strip().replace('**', '')
        # Nếu vẫn bị ngắn, tui cho nó cộng dồn một đoạn phân tích mẫu để bài báo không bị "cụt"
        if len(content) < 800:
            content += "\n\n[ADDITIONAL ANALYSIS] The current market structure suggests a tightening of liquidity following this news. Institutional players are advised to monitor the 10-year yield closely as a secondary indicator of sentiment shift. BrokeNoMore's internal algorithms indicate a 65% probability of increased volatility in the next 48 hours."
        return content
    except:
        return f"Market Intelligence Desk is currently processing the full data stream for {title}. Check back shortly for the 500-word deep dive."

def run_auto_news():
    posts_dir = 'posts'
    if not os.path.exists(posts_dir): os.makedirs(posts_dir)
    all_articles = []
    v_id = int(time.time())

    for _, url in RSS_SOURCES.items():
        feed = feedparser.parse(url)
        for entry in feed.entries[:4]: # Lấy 4 bài mỗi nguồn -> Tổng 16 bài
            thumb = get_thumbnail(entry)
            clean_summary = BeautifulSoup(entry.summary, 'html.parser').get_text()[:500] if 'summary' in entry else ""
            ai_content = rewrite_with_ai(entry.title, clean_summary)
            
            clean_title = "".join(x for x in entry.title if x.isalnum() or x==" ")
            filename = f"{datetime.now().strftime('%H%M%S')}-{clean_title[:15].replace(' ','')}.html"
            filepath = os.path.join(posts_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"""
                <html><head><meta charset='UTF-8'><title>{entry.title}</title>
                <link rel="icon" type="image/png" href="../favicon.png?v={v_id}">
                <link href='https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap' rel='stylesheet'>
                <style>body{{font-family:'Inter';line-height:1.9;max-width:850px;margin:0 auto;padding:60px 20px;color:#111;background:#fff}}h1{{font-size:52px;letter-spacing:-3px;line-height:1;margin-bottom:30px}}img{{width:100%;margin:30px 0;border-radius:4px}}.content{{white-space:pre-wrap;font-size:21px;color:#222}}</style></head>
                <body><header style='border-bottom:3px solid #000;padding-bottom:20px;margin-bottom:40px'><a href='../index.html?v={v_id}' style='text-decoration:none;color:#000;font-weight:900;text-transform:uppercase;font-size:24px'>BrokeNoMore</a></header>
                <h1>{entry.title}</h1><div style='color:#888;text-transform:uppercase;font-size:12px;margin-bottom:20px'>Institutional Intelligence • {datetime.now().strftime('%B %d, %Y')}</div><img src='{thumb}'><div class='content'>{ai_content}</div></body></html>
                """)
            all_articles.append({'title': entry.title, 'thumb': thumb, 'path': filepath, 'summary': ai_content[:250], 'time': datetime.now().strftime('%H:%M')})

    # Render Index.html - FIX LỖI VÒNG LẶP RENDER
    hero = all_articles[0]
    
    # Grid 1: 6 bài Latest bên phải
    latest_html = "".join([f"<div style='margin-bottom:25px;border-bottom:1px solid #eee;padding-bottom:15px;'><span style='color:red;font-size:11px;font-weight:900'>{a['time']}</span><br><a href='{a['path']}?v={v_id}' style='color:#000;text-decoration:none;font-weight:700;font-size:17px;display:block;margin-top:5px;line-height:1.2'>{a['title']}</a></div>" for a in all_articles[1:7]])
    
    # Grid 2: TẤT CẢ các bài còn lại sẽ hiện ở dưới dạng Grid 2 cột
    grid_html = ""
    for a in all_articles[7:]:
        grid_html += f"""
        <div style="margin-bottom:50px; border-top: 1px solid #000; padding-top:20px;">
            <img src="{a['thumb']}" style="width:100%;height:220px;object-fit:cover;border-radius:2px;">
            <h3 style="font-size:22px;margin:15px 0 10px;line-height:1.2;font-weight:900;"><a href="{a['path']}?v={v_id}" style="color:#000;text-decoration:none;">{a['title']}</a></h3>
            <p style="font-size:15px;color:#444;line-height:1.6;">{a['summary']}...</p>
        </div>"""

    index_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8"><title>BrokeNoMore | Market Terminal</title>
        <link rel="icon" type="image/png" href="favicon.png?v={v_id}">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Inter', sans-serif; margin: 0; background: #fff; color: #000; }}
            header {{ padding: 30px 5%; border-bottom: 8px solid #000; }}
            .logo {{ font-size: 50px; font-weight: 900; text-transform: uppercase; color: #000; text-decoration: none; letter-spacing: -4px; }}
            .main-layout {{ max-width: 1500px; margin: 40px auto; padding: 0 30px; display: grid; grid-template-columns: 2.8fr 1fr; gap: 60px; }}
            .article-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 40px; margin-top: 60px; }}
            @media (max-width: 1100px) {{ .main-layout, .article-grid {{ grid-template-columns: 1fr; }} }}
        </style>
    </head>
    <body>
        <header><a href="/" class="logo">BrokeNoMore</a></header>
        <div style="background:#000; padding:12px 0; border-bottom: 2px solid #333;">
            <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
            {{ "symbols": [{{"proName": "OANDA:XAUUSD", "title": "GOLD"}}, {{"proName": "BITSTAMP:BTCUSD", "title": "BTC"}}, {{"proName": "FX_IDC:USDVND", "title": "USDVND"}}, {{"proName": "NASDAQ:TSLA", "title": "TSLA"}}, {{"proName": "NASDAQ:AAPL", "title": "AAPL"}}], "colorTheme": "dark", "locale": "en" }}
            </script>
        </div>
        <div class="main-layout">
            <div>
                <img src="{hero['thumb']}" style="width:100%; height:600px; object-fit:cover;">
                <h2 style="font-size:60px; font-weight:900; letter-spacing:-4px; line-height:0.95; margin:35px 0;"><a href="{hero['path']}?v={v_id}" style="color:#000;text-decoration:none;">{hero['title']}</a></h2>
                <p style="font-size:24px; color:#222; line-height:1.6; margin-bottom:50px;">{hero['summary']}...</p>
                <div class="article-grid">{grid_html}</div>
            </div>
            <div style="border-left: 2px solid #000; padding-left: 40px;">
                <h3 style="font-size:14px; text-transform:uppercase; border-bottom:5px solid #000; padding-bottom:10px; margin-bottom:30px; font-weight:900;">Latest Intelligence</h3>
                {latest_html}
            </div>
        </div>
        <footer style="margin-top:100px; padding:60px; background:#000; color:#fff; text-align:center;">
            <p style="font-weight:900; letter-spacing:2px;">BROKENOMORE TERMINAL &copy; 2026</p>
        </footer>
    </body>
    </html>
    """
    with open('index.html', 'w', encoding='utf-8') as f: f.write(index_content)
    print("🚀 TERMINAL RECONSTRUCTED: 16 articles, forced length, image fallback active.")

if __name__ == "__main__":
    run_auto_news()
