import feedparser
import os
import random
import time
from datetime import datetime
from bs4 import BeautifulSoup
import google.generativeai as genai

# ==========================================
# 1. CẤU HÌNH (Sếp check kỹ API Key trong Secret nhé)
# ==========================================
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

RSS_SOURCES = {
    'Global': 'http://feeds.reuters.com/reuters/businessNews',
    'Markets': 'https://www.cnbc.com/id/10000667/device/rss/rss.html',
    'Institutional': 'https://feeds.a.dj.com/rss/WSJcomUSBusiness.xml'
}

def get_thumbnail(entry):
    # Dùng ảnh Stock theo chủ đề để không bao giờ bị trắng web
    stock_imgs = [
        f"https://picsum.photos/seed/{random.randint(1,999)}/800/500",
        "https://images.unsplash.com/photo-1611974717482-58a252c85aec?auto=format&fit=crop&w=800",
        "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?auto=format&fit=crop&w=800",
        "https://images.unsplash.com/photo-1640343830005-ee0505d307bb?auto=format&fit=crop&w=800"
    ]
    img = ""
    if 'media_content' in entry: img = entry.media_content[0]['url']
    elif 'enclosures' in entry and len(entry.enclosures) > 0: img = entry.enclosures[0]['url']
    
    if not img or "doubleclick" in img or "pixel" in img:
        return random.choice(stock_imgs)
    return img

def rewrite_with_ai(title, summary):
    # Nếu không có API Key thì dùng summary gốc luôn cho nhanh
    if not GOOGLE_API_KEY: return summary
    
    prompt = f"Act as BNM Senior Analyst. Write a 400-word financial report on: {title}. Context: {summary}. Use 3 sections: Context, Impact, Outlook. No bold."
    try:
        res = model.generate_content(prompt)
        text = res.text.strip().replace('**', '')
        if len(text) < 300: return summary + "\n\n" + "--- BNM Technical Note ---\n" + text
        return text
    except Exception as e:
        print(f"AI Error: {e}")
        return summary # Lỗi thì lấy summary gốc, đéo sợ bị trống nữa!

def run_auto_news():
    posts_dir = 'posts'
    if not os.path.exists(posts_dir): os.makedirs(posts_dir)
    all_articles = []
    v_id = int(time.time())

    for _, url in RSS_SOURCES.items():
        feed = feedparser.parse(url)
        for entry in feed.entries[:6]: # Lấy 18 tin tổng cộng
            thumb = get_thumbnail(entry)
            raw_desc = BeautifulSoup(entry.summary, 'html.parser').get_text() if 'summary' in entry else "Market data incoming..."
            ai_content = rewrite_with_ai(entry.title, raw_desc)
            
            clean_title = "".join(x for x in entry.title if x.isalnum() or x==" ")
            filename = f"{datetime.now().strftime('%H%M%S')}-{clean_title[:10]}.html"
            filepath = os.path.join(posts_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"""
                <html><head><meta charset='UTF-8'><title>{entry.title}</title>
                <link rel="icon" type="image/png" href="../favicon.png?v={v_id}">
                <link href='https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap' rel='stylesheet'>
                <style>body{{font-family:'Inter';line-height:1.9;max-width:850px;margin:0 auto;padding:60px 20px;color:#111;background:#fff}}
                h1{{font-size:48px;font-weight:900;letter-spacing:-3px;line-height:1.1;margin-bottom:30px}}
                img{{width:100%;border-radius:4px;margin:30px 0}} .content{{white-space:pre-wrap;font-size:20px}}</style></head>
                <body><a href="../index.html?v={v_id}" style="font-weight:900;text-decoration:none;color:#000">← TERMINAL</a>
                <h1>{entry.title}</h1><img src='{thumb}'><div class='content'>{ai_content}</div></body></html>
                """)
            all_articles.append({'title': entry.title, 'thumb': thumb, 'path': filepath, 'summary': ai_content[:250], 'time': datetime.now().strftime('%H:%M')})

    # Render Index.html (GIAO DIỆN SIÊU DÀY)
    hero = all_articles[0]
    side_html = "".join([f"<div style='margin-bottom:20px;border-bottom:1px solid #eee;padding-bottom:10px;'><span style='color:red;font-size:10px;font-weight:900'>{a['time']}</span><br><a href='{a['path']}?v={v_id}' style='color:#000;text-decoration:none;font-weight:700;font-size:15px'>{a['title']}</a></div>" for a in all_articles[1:7]])
    
    grid_html = ""
    for a in all_articles[7:]:
        grid_html += f"""
        <div style="margin-bottom:40px;">
            <img src="{a['thumb']}" style="width:100%;height:220px;object-fit:cover;border-radius:4px;">
            <h3 style="font-size:22px;margin:15px 0 10px;line-height:1.2;font-weight:900;"><a href="{a['path']}?v={v_id}" style="color:#000;text-decoration:none;">{a['title']}</a></h3>
            <p style="font-size:14px;color:#555;line-height:1.5;">{a['summary']}...</p>
        </div>"""

    index_content = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8"><title>BNM | Terminal</title>
        <link rel="icon" type="image/png" href="favicon.png?v={v_id}">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Inter', sans-serif; margin: 0; background: #fff; }}
            header {{ padding: 30px 5%; border-bottom: 8px solid #000; display: flex; align-items: center; justify-content: center; }}
            .logo {{ font-size: 50px; font-weight: 900; text-transform: uppercase; color: #000; text-decoration: none; letter-spacing: -4px; }}
            .container {{ max-width: 1500px; margin: 40px auto; padding: 0 30px; display: grid; grid-template-columns: 2.5fr 1fr; gap: 60px; }}
            .news-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 40px; margin-top: 50px; border-top: 6px solid #000; padding-top: 40px; }}
            @media (max-width: 1000px) {{ .container, .news-grid {{ grid-template-columns: 1fr; }} }}
        </style>
    </head>
    <body>
        <header><a href="/" class="logo">BrokeNoMore</a></header>
        <div style="background:#000; padding:12px 0;">
            <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
            {{ "symbols": [{{"proName": "OANDA:XAUUSD", "title": "GOLD"}}, {{"proName": "BITSTAMP:BTCUSD", "title": "BTC"}}, {{"proName": "FX_IDC:USDVND", "title": "USDVND"}}], "colorTheme": "dark", "locale": "en" }}
            </script>
        </div>
        <div class="container">
            <div>
                <img src="{hero['thumb']}" style="width:100%; height:550px; object-fit:cover;">
                <h2 style="font-size:55px; font-weight:900; letter-spacing:-3px; line-height:1; margin:30px 0;"><a href="{hero['path']}?v={v_id}" style="color:#000;text-decoration:none;">{hero['title']}</a></h2>
                <p style="font-size:22px; line-height:1.7; color:#333;">{hero['summary']}...</p>
                <div class="news-grid">{grid_html}</div>
            </div>
            <div style="border-left: 3px solid #000; padding-left: 40px;">
                <h3 style="font-size:14px; text-transform:uppercase; border-bottom:6px solid #000; padding-bottom:10px; margin-bottom:30px; font-weight:900;">Latest Intelligence</h3>
                {side_html}
            </div>
        </div>
    </body>
    </html>
    """
    with open('index.html', 'w', encoding='utf-8') as f: f.write(index_content)

if __name__ == "__main__":
    run_auto_news()
