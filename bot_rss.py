import feedparser, os, random, time, requests
from datetime import datetime
from bs4 import BeautifulSoup

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def build_pro_article(title, summary):
    expert_segments = [
        "The volatility in equity risk premiums is reaching a critical threshold.",
        "Institutional order flow shows heavy accumulation in defensive positions.",
        "From a technical perspective, the 200-day moving average is holding.",
        "The macro-economic backdrop remains clouded by central bank hawkishness."
    ]
    analysis = summary
    if GROQ_API_KEY:
        prompt = f"Write 500 words of expert financial analysis on: {title}. Context: {summary}. Use 4 long paragraphs. No bolding."
        try:
            headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
            payload = {"model": "llama3-70b-8192", "messages": [{"role": "user", "content": prompt}], "temperature": 0.5}
            res = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers, timeout=15).json()
            analysis = res['choices'][0]['message']['content'].replace('**', '')
        except: pass
    extra = "\n\n".join(random.sample(expert_segments, 2))
    return f"{analysis}\n\n{extra}\n\n[TERMINAL INTEL]: Asset rebalancing confirmed."

def run():
    posts_dir = 'posts'
    if not os.path.exists(posts_dir): os.makedirs(posts_dir)
    articles = []
    v = int(time.time())
    sources = ['https://www.cnbc.com/id/10000667/device/rss/rss.html', 'https://www.cnbc.com/id/19770192/device/rss/rss.html']
    
    for url in sources:
        feed = feedparser.parse(url)
        for e in feed.entries[:8]:
            # Dùng ảnh liên quan tài chính, tránh lỗi Unsplash
            img = f"https://placehold.co/800x450/111/fff?text=MARKET+DATA+{random.randint(10,99)}"
            summary_raw = BeautifulSoup(e.summary, 'html.parser').get_text()
            content = build_pro_article(e.title, summary_raw)
            fname = f"{datetime.now().strftime('%H%M%S')}-{random.randint(100,999)}.html"
            path = os.path.join(posts_dir, fname)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(f"""<html><head><meta charset='UTF-8'><link rel='icon' href='../favicon.ico'><style>
                body{{font-family:serif;max-width:900px;margin:0 auto;padding:60px 20px;line-height:1.9;background:#fff;color:#111}}
                h1{{font-size:55px;letter-spacing:-3px;line-height:0.95;margin-bottom:30px}}
                img{{width:100%;border-radius:2px;margin:30px 0;filter:grayscale(100%)}}
                p{{font-size:20px;text-align:justify;white-space:pre-wrap}}
                .back{{font-weight:900;text-decoration:none;color:#000;border-bottom:3px solid #000}}
                </style></head><body><a href='../index.html?v={v}' class='back'>← TERMINAL</a><h1>{e.title}</h1><img src='{img}'><p>{content}</p></body></html>""")
            articles.append({'t': e.title, 'p': path, 'img': img, 's': content[:200]})

    # Giao diện Index "Wall Street"
    hero = articles[0]
    grid_html = "".join([f"<div style='border-top:1px solid #000;padding-top:15px;'><a href='{a['p']}?v={v}' style='color:#000;text-decoration:none;'><img src='{a['img']}' style='width:100%;height:150px;object-fit:cover;filter:grayscale(100%);'><h3 style='font-size:18px;margin:10px 0;'>{a['t']}</h3></a></div>" for a in articles[1:7]])
    sidebar_html = "".join([f"<li style='margin-bottom:15px;list-style:none;border-bottom:1px solid #eee;padding-bottom:10px;'><a href='{a['p']}?v={v}' style='color:#000;text-decoration:none;font-weight:700;font-size:14px;'>{a['t']}</a></li>" for a in articles[7:15]])

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(f"""
        <!DOCTYPE html><html><head><meta charset='UTF-8'><link rel='icon' href='favicon.ico'><title>BNM TERMINAL</title><style>
        body{{font-family:'Times New Roman',serif;margin:0;background:#fefefe;color:#000}}
        header{{padding:30px 5%;border-bottom:10px solid #000;display:flex;justify-content:space-between;align-items:flex-end}}
        .container{{max-width:1300px;margin:30px auto;padding:0 20px;display:grid;grid-template-columns:3fr 1fr;gap:40px}}
        .hero-title{{font-size:60px;font-weight:900;line-height:0.9;letter-spacing:-4px;margin:20px 0}}
        .grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:25px;margin-top:40px}}
        </style></head><body>
        <div style='background:#000;height:40px;'><script type='text/javascript' src='https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js' async>{{ "symbols": [{{ "proName": "FX_IDC:XAUUSD", "title": "Gold" }}, {{ "proName": "BITSTAMP:BTCUSD", "title": "Bitcoin" }}, {{ "proName": "FX:EURUSD", "title": "EUR/USD" }}], "colorTheme": "dark" }}</script></div>
        <header><div style='font-size:60px;font-weight:900;letter-spacing:-5px;'>BROKENOMORE</div><div style='font-weight:900;'>{datetime.now().strftime('%B %d, %Y')}</div></header>
        <div class="container">
            <div>
                <div style='display:grid;grid-template-columns:1.5fr 1fr;gap:30px;border-bottom:4px solid #000;padding-bottom:30px;'>
                    <a href='{hero['p']}'><img src='{hero['img']}' style='width:100%;filter:grayscale(100%);'></a>
                    <div><h1 class='hero-title'><a href='{hero['p']}' style='color:#000;text-decoration:none;'>{hero['t']}</a></h1><p style='font-size:18px;'>{hero['s']}...</p></div>
                </div>
                <div class='grid'>{grid_html}</div>
            </div>
            <div style='border-left:2px solid #000;padding-left:20px;'>
                <h2 style='font-size:15px;text-transform:uppercase;border-bottom:4px solid #000;padding-bottom:5px;'>Latest Intelligence</h2>
                <ul style='padding:0;'>{sidebar_html}</ul>
            </div>
        </div></body></html>
        """)

if __name__ == "__main__": run()
