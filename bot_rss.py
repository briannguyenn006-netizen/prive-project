import feedparser, os, random, time, requests
from datetime import datetime
from bs4 import BeautifulSoup

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def build_pro_article(title, summary):
    # Những câu phân tích cực "deep" để AI trộn vào, tăng độ tin cậy
    expert_segments = [
        "The quantitative easing measures continue to distort the traditional yield curve, forcing a repositioning of long-duration assets.",
        "Institutional order flow shows a marked increase in dark pool activity near the current psychological resistance levels.",
        "Our proprietary sentiment index suggests that the retail long-short ratio is reaching an extreme, hinting at a potential squeeze.",
        "Technical indicators, specifically the weekly MACD, are showing a hidden bullish divergence that may catch the market off-guard."
    ]
    analysis = summary
    if GROQ_API_KEY:
        # Ép AI viết 500 chữ, dùng thuật ngữ chuyên môn cao
        prompt = f"Write a 500-word JAW-DROPPING financial deep-dive for: {title}. Context: {summary}. Tone: Senior Wall Street Strategist. Use 4-5 long paragraphs."
        try:
            headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
            payload = {"model": "llama3-70b-8192", "messages": [{"role": "user", "content": prompt}], "temperature": 0.6}
            res = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers, timeout=15).json()
            analysis = res['choices'][0]['message']['content'].replace('**', '').strip()
        except: pass

    # Trộn thêm 2 đoạn expert để bài viết dài ngoằng, bot quét mê ly
    extra = "\n\n".join(random.sample(expert_segments, 2))
    return f"{analysis}\n\n{extra}\n\n[BNM INTELLIGENCE]: Position sizing should be adjusted based on real-time volatility metrics."

def run():
    posts_dir = 'posts'
    if not os.path.exists(posts_dir): os.makedirs(posts_dir)
    articles = []
    v = int(time.time())
    
    # Lấy tin từ các nguồn CNBC xịn nhất
    sources = [
        'https://www.cnbc.com/id/10000667/device/rss/rss.html',
        'https://www.cnbc.com/id/100003114/device/rss/rss.html'
    ]
    
    for url in sources:
        feed = feedparser.parse(url)
        for e in feed.entries[:8]:
            # Dùng ảnh xám cho chất báo giấy tài chính
            img = f"https://placehold.co/800x450/000/fff?text=MARKET+INTEL+{random.randint(10,99)}"
            summary_raw = BeautifulSoup(e.summary, 'html.parser').get_text()
            content = build_pro_article(e.title, summary_raw)
            fname = f"{datetime.now().strftime('%H%M%S')}-{random.randint(100,999)}.html"
            path = os.path.join(posts_dir, fname)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(f"""<html><head><meta charset='UTF-8'><link rel='icon' href='../favicon.ico'><style>
                body{{font-family:serif;max-width:850px;margin:0 auto;padding:60px 20px;line-height:2;background:#fff;color:#111}}
                h1{{font-size:55px;font-weight:900;letter-spacing:-3px;line-height:0.95;margin-bottom:30px}}
                img{{width:100%;margin:30px 0;filter:grayscale(100%)}}
                p{{font-size:21px;text-align:justify;white-space:pre-wrap}}
                .back{{font-weight:900;text-decoration:none;color:#000;border-bottom:4px solid #000;padding-bottom:2px}}
                </style></head><body><a href='../index.html?v={v}' class='back'>← BACK TO TERMINAL</a><h1>{e.title}</h1><img src='{img}'><p>{content}</p></body></html>""")
            articles.append({'t': e.title, 'p': path, 'img': img, 's': content[:200], 'time': datetime.now().strftime('%H:%M')})

    # Render Index
    hero = articles[0]
    grid_html = "".join([f"<div style='border-top:2px solid #000;padding-top:15px;'><a href='{a['p']}?v={v}' style='color:#000;text-decoration:none;'><img src='{a['img']}' style='width:100%;height:160px;object-fit:cover;filter:grayscale(100%);'><h3 style='font-size:18px;margin:10px 0;line-height:1.2;'>{a['t']}</h3></a></div>" for a in articles[1:7]])
    sidebar_html = "".join([f"<li style='margin-bottom:15px;list-style:none;border-bottom:1px solid #eee;padding-bottom:10px;'><span style='font-size:10px;color:red;font-weight:900;'>{a['time']}</span><br><a href='{a['p']}?v={v}' style='color:#000;text-decoration:none;font-weight:700;font-size:14px;'>{a['t']}</a></li>" for a in articles[7:14]])

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(f"""
        <!DOCTYPE html><html><head><meta charset='UTF-8'><link rel='icon' href='favicon.ico'><title>BROKENOMORE TERMINAL</title><style>
        body{{font-family:'Times New Roman',serif;margin:0;background:#fff;color:#000}}
        header{{padding:30px 5%;border-bottom:10px solid #000;display:flex;justify-content:space-between;align-items:flex-end}}
        .container{{max-width:1400px;margin:30px auto;padding:0 20px;display:grid;grid-template-columns:3fr 1fr;gap:50px}}
        .hero-title{{font-size:65px;font-weight:900;line-height:0.9;letter-spacing:-4px;margin:20px 0}}
        .grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:30px;margin-top:40px}}
        </style></head><body>
        <div style='background:#000;height:40px;'><script type='text/javascript' src='https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js' async>{{ "symbols": [{{ "proName": "FX_IDC:XAUUSD", "title": "Gold" }}, {{ "proName": "BITSTAMP:BTCUSD", "title": "Bitcoin" }}, {{ "proName": "FX:EURUSD", "title": "EUR/USD" }}], "colorTheme": "dark", "isTransparent": true }}</script></div>
        <header><div style='font-size:70px;font-weight:900;letter-spacing:-6px;'>BROKENOMORE</div><div style='font-weight:900;text-transform:uppercase;'>{datetime.now().strftime('%B %d, %Y')}</div></header>
        <div class="container">
            <div>
                <div style='display:grid;grid-template-columns:1.6fr 1fr;gap:40px;border-bottom:5px solid #000;padding-bottom:40px;'>
                    <a href='{hero['p']}'><img src='{hero['img']}' style='width:100%;filter:grayscale(100%);'></a>
                    <div><h1 class='hero-title'><a href='{hero['p']}' style='color:#000;text-decoration:none;'>{hero['t']}</a></h1><p style='font-size:20px;line-height:1.5;'>{hero['s']}...</p></div>
                </div>
                <div class='grid'>{grid_html}</div>
            </div>
            <div style='border-left:3px solid #000;padding-left:30px;'>
                <h2 style='font-size:14px;text-transform:uppercase;border-bottom:5px solid #000;padding-bottom:5px;margin-bottom:20px;font-weight:900;'>Latest Intelligence</h2>
                <ul style='padding:0;margin:0;'>{sidebar_html}</ul>
            </div>
        </div></body></html>
        """)

if __name__ == "__main__": run()
