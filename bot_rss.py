import feedparser, os, random, time, requests
from datetime import datetime
from bs4 import BeautifulSoup

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def analyze_ultra_force(title, summary):
    backup_text = f"Market volatility is driving price action for {title}. Institutional desks are monitoring liquidity levels closely. Strategic shifts in risk parity and equity premiums are expected as the session progresses. BNM Terminal suggests maintaining a high-conviction stance."
    if not GROQ_API_KEY: return backup_text
    
    prompt = f"Write a 400-word financial analysis for: {title}. Context: {summary}. Use 3-4 long paragraphs. No bolding. Tone: Wall Street Elite."
    try:
        payload = {"model": "llama3-70b-8192", "messages": [{"role": "user", "content": prompt}], "temperature": 0.6}
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers, timeout=15)
        content = response.json()['choices'][0]['message']['content'].replace('**', '').strip()
        return content if len(content) > 300 else content + "\n\n" + backup_text
    except: return backup_text

def run():
    posts_dir = 'posts'
    if not os.path.exists(posts_dir): os.makedirs(posts_dir)
    articles = []
    v = int(time.time())
    
    # Lấy từ 3 nguồn để tin tức ĐÈ CHẾT NGƯỜI
    sources = [
        'https://www.cnbc.com/id/10000667/device/rss/rss.html',
        'https://www.cnbc.com/id/100003114/device/rss/rss.html',
        'https://www.cnbc.com/id/19854910/device/rss/rss.html'
    ]
    
    for url in sources:
        feed = feedparser.parse(url)
        for e in feed.entries[:6]: # Mỗi nguồn lấy 6 tin = 18 tin tổng cộng
            img = f"https://picsum.photos/seed/{random.randint(1,99999)}/800/500"
            summary_raw = BeautifulSoup(e.summary, 'html.parser').get_text()
            full_text = analyze_ultra_force(e.title, summary_raw)
            fname = f"{datetime.now().strftime('%H%M%S')}-{random.randint(100,999)}.html"
            path = os.path.join(posts_dir, fname)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(f"<html><head><meta charset='UTF-8'><link rel='icon' href='../favicon.png?v={v}'><link href='https://fonts.googleapis.com/css2?family=Inter:wght@400;900&display=swap' rel='stylesheet'><style>body{{font-family:Inter;max-width:800px;margin:0 auto;padding:60px 20px;line-height:1.8;color:#111;background:#fff}}h1{{font-size:45px;font-weight:900;letter-spacing:-3px;line-height:1}}img{{width:100%;margin:30px 0;border-radius:4px}}p{{font-size:19px;text-align:justify;white-space:pre-wrap}}</style></head><body><a href='../index.html?v={v}' style='text-decoration:none;color:#000;font-weight:900'>← TERMINAL</a><h1>{e.title}</h1><img src='{img}'><p>{full_text}</p></body></html>")
            articles.append({'t': e.title, 'p': path, 's': full_text[:150], 'img': img, 'time': datetime.now().strftime('%H:%M')})

    # Render Index
    hero = articles[0]
    side_html = "".join([f"<div style='margin-bottom:15px;border-bottom:1px solid #eee;padding-bottom:10px;'><span style='color:red;font-size:10px;font-weight:900;'>{a['time']}</span><br><a href='{a['p']}?v={v}' style='color:#000;text-decoration:none;font-weight:700;font-size:13px;'>{a['t']}</a></div>" for a in articles[1:15]])
    grid_html = "".join([f"<div style='margin-bottom:20px;'><img src='{a['img']}' style='width:100%;height:150px;object-fit:cover;border-radius:2px;'><h3 style='font-size:14px;font-weight:900;margin:10px 0;'><a href='{a['p']}?v={v}' style='color:#000;text-decoration:none;'>{a['t']}</a></h3></div>" for a in articles[1:7]])

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(f"""
        <!DOCTYPE html><html><head><meta charset='UTF-8'><title>BNM Terminal</title><link rel='icon' href='favicon.png?v={v}'><link href='https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap' rel='stylesheet'><style>
        body{{font-family:Inter;margin:0;background:#fff;color:#000}}
        header{{padding:20px 5%;border-bottom:8px solid #000;display:flex;justify-content:space-between;align-items:center}}
        .logo{{font-size:40px;font-weight:900;text-decoration:none;color:#000;letter-spacing:-3px;text-transform:uppercase}}
        .container{{max-width:1400px;margin:30px auto;padding:0 20px;display:grid;grid-template-columns:2.8fr 1fr;gap:40px}}
        .grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin-top:30px;border-top:4px solid #000;padding-top:20px}}
        </style></head><body>
        <header><a href='/' class='logo'>BrokeNoMore</a><div style='font-weight:900;font-size:12px'>LIVE TERMINAL // {datetime.now().strftime('%Y-%m-%d')}</div></header>
        <div style='background:#000;padding:8px 0'><script type='text/javascript' src='https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js' async>{{ "symbols": [{{ "proName": "OANDA:XAUUSD", "title": "GOLD" }}, {{ "proName": "BITSTAMP:BTCUSD", "title": "BTC" }}] }}</script></div>
        <div class="container">
            <div>
                <div style='display:grid;grid-template-columns:1.5fr 1fr;gap:30px'>
                    <a href='{hero['p']}?v={v}'><img src='{hero['img']}' style='width:100%;height:400px;object-fit:cover;'></a>
                    <div><h1 style='font-size:40px;font-weight:900;margin:0 0 20px;line-height:1'><a href='{hero['p']}?v={v}' style='color:#000;text-decoration:none;'>{hero['t']}</a></h1><p style='font-size:16px;line-height:1.6'>{hero['s']}...</p></div>
                </div>
                <div class='grid'>{grid_html}</div>
            </div>
            <div style='border-left:3px solid #000;padding-left:25px'>
                <h3 style='font-size:12px;text-transform:uppercase;border-bottom:6px solid #000;padding-bottom:10px;margin-bottom:20px;font-weight:900'>Latest Intelligence</h3>
                {side_html}
            </div>
        </div></body></html>
        """)

if __name__ == "__main__": run()
