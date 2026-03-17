import feedparser
import os
import random
import time
from datetime import datetime
from bs4 import BeautifulSoup
import google.generativeai as genai

# ==========================================
# THIẾT LẬP CHIẾN THUẬT
# ==========================================
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

RSS_SOURCES = {
    'Global': 'http://feeds.reuters.com/reuters/businessNews',
    'Tech': 'https://www.cnbc.com/id/19854910/device/rss/rss.html',
    'Markets': 'https://www.cnbc.com/id/10000667/device/rss/rss.html'
}

def get_thumbnail(entry):
    # Dùng ảnh stock chất lượng cao để lấp đầy layout nếu ảnh gốc lỗi
    stock_imgs = [
        f"https://picsum.photos/seed/{random.randint(1,1000)}/800/500",
        "https://images.unsplash.com/photo-1611974717482-58a252c85aec?q=80&w=800",
        "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?q=80&w=800",
        "https://images.unsplash.com/photo-1640343830005-ee0505d307bb?q=80&w=800"
    ]
    img = ""
    if 'media_content' in entry: img = entry.media_content[0]['url']
    elif 'enclosures' in entry and len(entry.enclosures) > 0: img = entry.enclosures[0]['url']
    
    if not img or "doubleclick" in img or "pixel" in img:
        return random.choice(stock_imgs)
    return img

def rewrite_with_ai(title, summary):
    # Prompt bạo lực: Ép AI viết ít nhất 500 từ, không được dùng từ 'pending'
    prompt = f"""
    Write a COMPREHENSIVE 500-word financial analysis for: {title}. 
    Context: {summary}.
    
    REQUIREMENTS:
    - Act as a Senior Hedge Fund Manager at BrokeNoMore.
    - 3 Huge Sections: [Executive Summary], [Market Volatility Analysis], [Strategic Implementation].
    - Tone: Extremely professional, data-heavy, cold.
    - NO bolding (**). NO citations. 
    - MANDATORY: Minimum 5 paragraphs. If you write less than 400 words, you fail.
    """
    try:
        res = model.generate_content(prompt)
        text = res.text.strip().replace('**', '')
        if len(text) < 500: # Nếu AI vẫn lười, ép nó lần nữa bằng cách lặp nội dung
             return text + "\n\n" + text[:300] + "... [Analysis Extended by BNM Desk]"
        return text
    except:
        return "Critical analysis unavailable. Desk is manually processing the data stream for " + title

def run_auto_news():
    posts_dir = 'posts'
    if not os.path.exists(posts_dir): os.makedirs(posts_dir)
    all_articles = []
    v_id = int(time.time())

    # Lấy tổng cộng 18 bài để fill cho sướng mắt
    for _, url in RSS_SOURCES.items():
        feed = feedparser.parse(url)
        for entry in feed.entries[:6]: 
            thumb = get_thumbnail(entry)
            summary_raw = BeautifulSoup(entry.summary, 'html.parser').get_text()[:400]
            ai_content = rewrite_with_ai(entry.title, summary_raw)
            
            clean_title = "".join(x for x in entry.title if x.isalnum() or x==" ")
            filename = f"{datetime.now().strftime('%H%M%S')}-{clean_title[:10]}.html"
            filepath = os.path.join(posts_dir, filename)
            
            # Sub-page layout (Bloomberg Style)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"""
                <html><head><meta charset='UTF-8'><title>{entry.title}</title>
                <link rel="icon" type="image/png" href="../favicon.png?v={v_id}">
                <link href='https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap' rel='stylesheet'>
                <style>body{{font-family:'Inter';line-height:1.9;max-width:850px;margin:0 auto;padding:60px 20px;color:#111}}h1{{font-size:52px;font-weight:900;letter-spacing:-3px;line-height:1;margin-bottom:30px}}img{{width:100%;margin:40px 0;border-radius:4px}}.content{{white-space:pre-wrap;font-size:20px}}</style></head>
                <body><a href="../index.html?v={v_id}" style="font-weight:900;text-decoration:none;color:#000">← BNM TERMINAL</a><h1>{entry.title}</h1><div style='color:#888;margin-bottom:20px'>INTEL • {datetime.now().strftime('%H:%M')}</div><img src='{thumb}'><div class='content'>{ai_content}</div></body></html>
                """)
            all_articles.append({'title': entry.title, 'thumb': thumb, 'path': filepath, 'summary': ai_content[:250], 'time': datetime.now().strftime('%H:%M')})

    # PHẦN QUAN TRỌNG: RENDER INDEX (MULTI-GRID)
    hero = all_articles[0]
    
    # 1. Cột Latest (7 bài)
    side_news = "".join([f"<div style='margin-bottom:20px;border-bottom:1px solid #eee;padding-bottom:10px;'><span style='color:red;font-size:10px;font-weight:900'>{a['time']}</span><br><a href='{a['path']}?v={v_id}' style='color:#000;text-decoration:none;font-weight:700;font-size:15px'>{a['title']}</a></div>" for a in all_articles[1:8]])
    
    # 2. Lưới Grid (Tất cả bài còn lại)
    grid_html = ""
    for a in all_articles[8:]:
        grid_html += f"""
        <div style="margin-bottom:40px;">
            <img src="{a['thumb']}" style="width:100%;height:220px;object-fit:cover;border-radius:2px;">
            <h3 style="font-size:22px;margin:15px 0 10px;line-height:1.2;font-weight:900;"><a href="{a['path']}?v={v_id}" style="color:#000;text-decoration:none;">{a['title']}</a></h3>
            <p style="font-size:14px;color:#555;line-height:1.5;">{a['summary']}...</p>
        </div>"""

    index_content = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8"><title>BrokeNoMore | Terminal</title>
        <link rel="icon" type="image/png" href="favicon.png?v={v_id}">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Inter', sans-serif; margin: 0; background: #fff; color: #111; }}
            header {{ padding: 25px 5%; border-bottom: 6px solid #000; display: flex; align-items: center; justify-content: center; }}
            .logo {{ font-size: 50px; font-weight: 900; text-transform: uppercase; color: #000; text-decoration: none; letter-spacing: -4px; }}
            .main-container {{ max-width: 1450px; margin: 40px auto; padding: 0 25px; display: grid; grid-template-columns: 2.4fr 1fr; gap: 60px; }}
            .news-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 40px; margin-top: 50px; border-top: 5px solid #000; padding-top: 40px; }}
            @media (max-width: 1000px) {{ .main-container, .news-grid {{ grid-template-columns: 1fr; }} }}
        </style>
    </head>
    <body>
        <header><a href="/" class="logo">BrokeNoMore</a></header>
        <div style="background:#000; padding:12px 0;">
            <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
            {{ "symbols": [{{"proName": "OANDA:XAUUSD", "title": "GOLD"}}, {{"proName": "BITSTAMP:BTCUSD", "title": "BTC"}}, {{"proName": "FX_IDC:USDVND", "title": "USDVND"}}, {{"proName": "NASDAQ:TSLA", "title": "TSLA"}}], "colorTheme": "dark", "locale": "en" }}
            </script>
        </div>
        <div class="main-container">
            <div>
                <img src="{hero['thumb']}" style="width:100%; height:580px; object-fit:cover;">
                <h2 style="font-size:55px; font-weight:900; letter-spacing:-3px; line-height:1; margin:30px 0;"><a href="{hero['path']}?v={v_id}" style="color:#000;text-decoration:none;">{hero['title']}</a></h2>
                <p style="font-size:22px; line-height:1.7; color:#333;">{hero['summary']}...</p>
                <div class="news-grid">{grid_html}</div>
            </div>
            <div style="border-left: 2px solid #000; padding-left: 40px;">
                <h3 style="font-size:14px; text-transform:uppercase; border-bottom:5px solid #000; padding-bottom:10px; margin-bottom:30px; font-weight:900;">Intelligence Stream</h3>
                {side_news}
            </div>
        </div>
    </body>
    </html>
    """
    with open('index.html', 'w', encoding='utf-8') as f: f.write(index_content)
    print("🚀 TERMINAL RECONSTRUCTED. READY FOR DEPLOY.")

if __name__ == "__main__":
    run_auto_news()
