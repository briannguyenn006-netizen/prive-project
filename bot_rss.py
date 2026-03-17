import feedparser
import os
import re
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

RSS_SOURCES = {
    'Global': 'http://feeds.reuters.com/reuters/businessNews',
    'Markets': 'https://www.cnbc.com/id/10000667/device/rss/rss.html',
    'Trends': 'https://feeds.a.dj.com/rss/WSJcomUSBusiness.xml'
}

# Fix ảnh lỗi bằng Stock xịn
def get_thumbnail(entry):
    stock_imgs = [
        "https://images.unsplash.com/photo-1611974717482-58a252c85aec?w=800&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=800&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1640343830005-ee0505d307bb?w=800&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1633156191771-700947264a2c?w=800&auto=format&fit=crop"
    ]
    img = ""
    if 'media_content' in entry: img = entry.media_content[0]['url']
    elif 'enclosures' in entry and len(entry.enclosures) > 0: img = entry.enclosures[0]['url']
    
    if not img or any(x in img for x in ["doubleclick", "pixel", "feedburner"]):
        return random.choice(stock_imgs)
    return img

def rewrite_with_ai(title, summary):
    prompt = f"Act as BNM Analyst. Write a 350-word deep-dive report on: {title}. Context: {summary}. Use 3 clear sections: Overview, Impact, Outlook. No bold."
    try:
        res = model.generate_content(prompt)
        return res.text.strip().replace('**', '') if len(res.text) > 400 else f"Expansion of {title} in progress..."
    except:
        return f"Institutional analysis for {title} is pending internal review."

def run_auto_news():
    posts_dir = 'posts'
    if not os.path.exists(posts_dir): os.makedirs(posts_dir)
    all_articles = []
    v_id = int(time.time())

    for _, url in RSS_SOURCES.items():
        feed = feedparser.parse(url)
        for entry in feed.entries[:4]: # Lấy 4 bài mỗi nguồn cho nó nhiều
            thumb = get_thumbnail(entry)
            clean_summary = BeautifulSoup(entry.summary, 'html.parser').get_text()[:300] if 'summary' in entry else ""
            ai_content = rewrite_with_ai(entry.title, clean_summary)
            
            clean_title = "".join(x for x in entry.title if x.isalnum() or x==" ")
            filename = f"{datetime.now().strftime('%H%M%S')}-{clean_title[:15]}.html"
            filepath = os.path.join(posts_dir, filename)
            
            # Sub-page layout
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"""
                <html><head><meta charset='UTF-8'><title>{entry.title}</title>
                <link rel="icon" type="image/png" href="../favicon.png?v={v_id}">
                <link href='https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap' rel='stylesheet'>
                <style>body{{font-family:'Inter';line-height:1.7;max-width:800px;margin:0 auto;padding:50px 20px;color:#111}}h1{{font-size:45px;letter-spacing:-2px;line-height:1.1}}img{{width:100%;border-radius:4px}} .content{{white-space:pre-wrap;font-size:19px}}</style></head>
                <body><a href="../index.html?v={v_id}" style="text-decoration:none;color:#000;font-weight:900">← TERMINAL</a><h1>{entry.title}</h1><img src='{thumb}'><div class='content'>{ai_content}</div></body></html>
                """)
            all_articles.append({'title': entry.title, 'thumb': thumb, 'path': filepath, 'summary': ai_content[:150], 'time': datetime.now().strftime('%H:%M')})

    # Render Index.html - MULTI-GRID LAYOUT
    hero = all_articles[0]
    latest_list = "".join([f"<div style='margin-bottom:20px;border-bottom:1px solid #eee;padding-bottom:10px;'><span style='color:red;font-size:11px;font-weight:900'>{a['time']}</span><br><a href='{a['path']}?v={v_id}' style='color:#000;text-decoration:none;font-weight:700;font-size:16px'>{a['title']}</a></div>" for a in all_articles[1:7]])
    
    grid_items = ""
    for a in all_articles[7:]:
        grid_items += f"""
        <div style="margin-bottom:30px;">
            <img src="{a['thumb']}" style="width:100%;height:180px;object-fit:cover;border-radius:4px;">
            <h4 style="margin:10px 0 5px;"><a href="{a['path']}?v={v_id}" style="color:#000;text-decoration:none;">{a['title']}</a></h4>
            <p style="font-size:13px;color:#666;">{a['summary']}...</p>
        </div>"""

    index_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8"><title>BNM Terminal</title>
        <link rel="icon" type="image/png" href="favicon.png?v={v_id}">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Inter', sans-serif; margin: 0; background: #fff; }}
            header {{ padding: 30px 5%; border-bottom: 5px solid #000; }}
            .logo {{ font-size: 36px; font-weight: 900; text-transform: uppercase; color: #000; text-decoration: none; letter-spacing: -2px; }}
            .container {{ max-width: 1400px; margin: 40px auto; padding: 0 20px; display: grid; grid-template-columns: 2.5fr 1fr; gap: 50px; }}
            .grid-container {{ display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-top: 50px; border-top: 3px solid #000; padding-top: 30px; }}
            @media (max-width: 900px) {{ .container, .grid-container {{ grid-template-columns: 1fr; }} }}
        </style>
    </head>
    <body>
        <header><a href="/" class="logo">BrokeNoMore</a></header>
        <div style="background:#000; padding:10px 0;">
            <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
            {{ "symbols": [{{"proName": "OANDA:XAUUSD", "title": "GOLD"}}, {{"proName": "BITSTAMP:BTCUSD", "title": "BTC"}}, {{"proName": "FX_IDC:USDVND", "title": "USDVND"}}], "colorTheme": "dark", "locale": "en" }}
            </script>
        </div>
        <div class="container">
            <div>
                <img src="{hero['thumb']}" style="width:100%; height:550px; object-fit:cover; border-radius:4px;">
                <h2 style="font-size:48px; font-weight:900; letter-spacing:-2.5px; line-height:1; margin:25px 0;"><a href="{hero['path']}?v={v_id}" style="color:#000;text-decoration:none;">{hero['title']}</a></h2>
                <p style="font-size:20px; line-height:1.6; color:#333;">{hero['summary']}...</p>
                <div class="grid-container">{grid_items}</div>
            </div>
            <div style="border-left: 1px solid #eee; padding-left: 30px;">
                <h3 style="font-size:12px; text-transform:uppercase; border-bottom:3px solid #000; padding-bottom:5px; margin-bottom:25px; font-weight:900;">Latest Intelligence</h3>
                {latest_list}
            </div>
        </div>
    </body>
    </html>
    """
    with open('index.html', 'w', encoding='utf-8') as f: f.write(index_content)

if __name__ == "__main__":
    run_auto_news()
