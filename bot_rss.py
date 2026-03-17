import feedparser, os, random, time, google.generativeai as genai
from datetime import datetime
from bs4 import BeautifulSoup

# ==========================================
# BNM CORE CONFIGURATION
# ==========================================
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

RSS_SOURCES = {
    'Markets': 'https://www.cnbc.com/id/10000667/device/rss/rss.html',
    'Tech': 'https://www.cnbc.com/id/19854910/device/rss/rss.html',
    'Finance': 'https://www.cnbc.com/id/100003114/device/rss/rss.html'
}

def get_smart_image(title):
    # Trích xuất từ khóa từ tiêu đề để lấy ảnh liên quan
    keywords = ["finance", "trading", "stock", "market"]
    important_words = [word for word in title.split() if len(word) > 4]
    search_query = important_words[0] if important_words else "business"
    return f"https://source.unsplash.com/featured/800x500?{search_query},corporate"

def analyze_news(title, raw_context):
    if not GOOGLE_API_KEY: return raw_context
    
    prompt = f"""
    You are the Lead Strategist at BrokeNoMore (BNM). 
    Analyze this news: {title}
    Context: {raw_context}
    
    REQUIREMENTS:
    - Write exactly 4 paragraphs (400-500 words).
    - Paragraph 1: Executive Summary & Market Reaction.
    - Paragraph 2: Deep Fundamental Analysis.
    - Paragraph 3: Institutional Investor Sentiment.
    - Paragraph 4: Final BNM Strategic Recommendation.
    - Tone: Sophisticated, Professional, English only.
    - Strictly NO bold (**) symbols.
    """
    
    for _ in range(3): # Ép AI làm việc nghiêm túc
        try:
            res = model.generate_content(prompt)
            content = res.text.replace('**', '').strip()
            if len(content) > 1200: return content # Đảm bảo độ dài tối thiểu
        except: continue
    return raw_context

def run_terminal():
    posts_dir = 'posts'
    if not os.path.exists(posts_dir): os.makedirs(posts_dir)
    articles = []
    v = int(time.time())

    for _, url in RSS_SOURCES.items():
        feed = feedparser.parse(url)
        for entry in feed.entries[:5]:
            img = get_smart_image(entry.title)
            summary = BeautifulSoup(entry.summary, 'html.parser').get_text()
            full_analysis = analyze_news(entry.title, summary)
            
            slug = "".join(x for x in entry.title if x.isalnum())[:20]
            fname = f"{datetime.now().strftime('%H%M%S')}-{slug}.html"
            fpath = os.path.join(posts_dir, fname)
            
            # Sub-page (Bản tin chi tiết)
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(f"""
                <html><head><meta charset='UTF-8'><title>{entry.title} | BNM</title>
                <link rel="icon" type="image/png" href="../favicon.png?v={v}">
                <link href='https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap' rel='stylesheet'>
                <style>
                    body{{font-family:'Inter';max-width:850px;margin:0 auto;padding:60px 20px;line-height:1.9;color:#111;background:#fff}}
                    .back{{font-weight:900;text-decoration:none;color:#000;font-size:14px;text-transform:uppercase}}
                    h1{{font-size:48px;font-weight:900;letter-spacing:-3px;line-height:1.1;margin:30px 0}}
                    img{{width:100%;border-radius:4px;margin-bottom:40px}}
                    .analysis{{white-space:pre-wrap;font-size:20px;text-align:justify}}
                </style></head>
                <body><a href='../index.html?v={v}' class='back'>← Return to Market Terminal</a>
                <h1>{entry.title}</h1><img src='{img}'><div class='analysis'>{full_analysis}</div></body></html>
                """)
            articles.append({'t': entry.title, 'p': fpath, 's': full_analysis[:220], 'img': img, 'time': datetime.now().strftime('%H:%M')})

    # Render Index.html
    hero = articles[0]
    latest_list = "".join([f"<div style='margin-bottom:20px;border-bottom:1px solid #eee;padding-bottom:15px;'><span style='color:red;font-size:11px;font-weight:900;'>{a['time']}</span><br><a href='{a['p']}?v={v}' style='color:#000;text-decoration:none;font-weight:700;font-size:15px;'>{a['t']}</a></div>" for a in articles[1:8]])
    grid_cards = "".join([f"<div style='margin-bottom:40px;'><img src='{a['img']}' style='width:100%;height:250px;object-fit:cover;'><h3 style='font-size:22px;margin:15px 0 10px;font-weight:900;'><a href='{a['p']}?v={v}' style='color:#000;text-decoration:none;'>{a['t']}</a></h3><p style='font-size:15px;color:#555;'>{a['s']}...</p></div>" for a in articles[8:]])

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(f"""
        <!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
        <title>BrokeNoMore | Terminal</title>
        <link rel="icon" type="image/png" href="favicon.png?v={v}">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Inter', sans-serif; margin: 0; background: #fff; }}
            header {{ padding: 30px 5%; border-bottom: 8px solid #000; }}
            .logo {{ font-size: 45px; font-weight: 900; text-transform: uppercase; color: #000; text-decoration: none; letter-spacing: -3px; }}
            .container {{ max-width: 1400px; margin: 40px auto; padding: 0 30px; display: grid; grid-template-columns: 2.5fr 1fr; gap: 60px; }}
            .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 40px; margin-top: 50px; border-top: 5px solid #000; padding-top: 40px; }}
            @media (max-width: 1000px) {{ .container, .grid {{ grid-template-columns: 1fr; }} }}
        </style></head>
        <body>
            <header><a href="/" class="logo">BrokeNoMore</a></header>
            <div style="background:#000; padding:12px 0;"><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>{{ "symbols": [{{"proName": "OANDA:XAUUSD", "title": "GOLD"}}, {{"proName": "BITSTAMP:BTCUSD", "title": "BTC"}}]}}</script></div>
            <div class="container">
                <div>
                    <img src="{hero['img']}" style="width:100%; height:550px; object-fit:cover;">
                    <h2 style="font-size:55px; font-weight:900; letter-spacing:-3px; margin:30px 0; line-height:1;"><a href="{hero['p']}?v={v}" style="color:#000;text-decoration:none;">{hero['t']}</a></h2>
                    <p style="font-size:22px; color:#333;">{hero['s']}...</p>
                    <div class="grid">{grid_cards}</div>
                </div>
                <div style="border-left: 3px solid #000; padding-left: 40px;">
                    <h3 style="font-size:14px; text-transform:uppercase; border-bottom:6px solid #000; padding-bottom:10px; margin-bottom:30px; font-weight:900;">Latest</h3>
                    {latest_list}
                </div>
            </div>
        </body></html>
        """)

if __name__ == "__main__":
    run_terminal()
