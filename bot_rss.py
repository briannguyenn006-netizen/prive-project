import feedparser, os, random, time, requests
from datetime import datetime

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
FAVICON_PATH = "favicon.png"

def build_pro_article(title, summary):
    if not GROQ_API_KEY: return summary
    prompt = f"""
    Act as a Senior Market Strategist. Write a 1000-word premium intelligence report on: "{title}".
    Context: {summary}
    Style: Bloomberg Terminal, institutional grade. No bolding (**).
    """
    try:
        res = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={"model": "llama3-70b-8192", "messages": [{"role": "user", "content": prompt}], "temperature": 0.5}, timeout=30).json()
        return res['choices'][0]['message']['content'].strip()
    except: return summary

def run():
    posts_dir = 'posts'
    if not os.path.exists(posts_dir): os.makedirs(posts_dir)
    for f in os.listdir(posts_dir):
        try: os.remove(os.path.join(posts_dir, f))
        except: pass
    
    feed = feedparser.parse('https://www.cnbc.com/id/10000667/device/rss/rss.html')
    articles = []
    v = int(time.time())

    # TRADINGVIEW (Chỉ dành cho trang chủ)
    tv_ticker = """
    <div style="background:#000; border-bottom:1px solid #333; height: 40px; overflow: hidden;">
        <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
        {
          "symbols": [
            {"proName": "BITSTAMP:BTCUSD", "title": "Bitcoin"},
            {"proName": "FX_IDC:XAUUSD", "title": "Gold"},
            {"proName": "FOREXCOM:SPX500", "title": "S&P 500"},
            {"proName": "NASDAQ:TSLA", "title": "Tesla"}
          ],
          "showSymbolLogo": true, "colorTheme": "dark", "isTransparent": true, "displayMode": "adaptive", "locale": "en"
        }
        </script>
    </div>
    """

    for i, e in enumerate(feed.entries[:12]):
        img = f"https://picsum.photos/seed/bnm_artsy_{i}/1200/800"
        content = build_pro_article(e.title, e.summary)
        fname = f"news-{i}.html"
        path = os.path.join(posts_dir, fname)
        
        # TRANG BÀI VIẾT: BỎ TRADINGVIEW, FIX LOGO VÀ CHỮ
        with open(path, 'w', encoding='utf-8') as f:
            f.write(f"""<html><head><meta charset='UTF-8'><link rel='icon' href='../{FAVICON_PATH}'><title>{e.title}</title>
            <style>
                body{{background:#000;color:#ccc;font-family:serif;padding:0;margin:0;line-height:1.8;}} 
                .content-wrap{{max-width:850px;margin:auto;padding:60px 20px;}}
                .nav{{display:flex;align-items:center;gap:12px;color:#fbbf24;text-decoration:none;font-weight:900;font-family:sans-serif;font-size:13px;text-transform:uppercase}}
                .news-logo{{ width: 35px; height: 35px; object-fit: contain; }}
                h1{{color:#fff;font-size:48px;font-family:sans-serif;font-weight:900;letter-spacing:-2px;margin:30px 0;line-height:1.0}} 
                img{{width:100%;border:1px solid #333;margin:40px 0;filter: grayscale(100%)}} 
                p{{font-size:20px;text-align:justify;white-space:pre-wrap}}
            </style></head>
            <body>
            <div class='content-wrap'>
                <a href='../index.html?v={v}' class='nav'><img src='../{FAVICON_PATH}' class='news-logo'> Back To Terminal</a>
                <h1>{e.title}</h1>
                <div style='color:#fbbf24;font-family:sans-serif;font-weight:bold;font-size:12px;letter-spacing:1px'>INTEL REPORT // BrokeNoMore // CLASSIFIED</div>
                <img src='{img}'>
                <p>{content}</p>
            </div></body></html>""")
        articles.append({'t': e.title, 'p': path, 'img': img, 'time': datetime.now().strftime('%H:%M')})

    hero = articles[0]
    grid_html = "".join([f"<div style='margin-bottom:30px;border-bottom:1px solid #222;padding-bottom:20px'><a href='./{a['p']}' style='color:#fff;text-decoration:none'><img src='{a['img']}' style='width:100%;height:180px;object-fit:cover;border:1px solid #333;filter:grayscale(100%)'><h3 style='font-size:17px;margin-top:12px;line-height:1.2;font-weight:900'>{a['t']}</h3></a></div>" for a in articles[1:5]])

    # TRANG CHỦ: CÓ TRADINGVIEW, ĐỔI TÊN THÀNH BrokeNoMore
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(f"""<!DOCTYPE html><html><head><meta charset='UTF-8'><link rel='icon' href='{FAVICON_PATH}'><title>BrokeNoMore Terminal</title>
        <style>
            body{{background:#000;color:#fff;font-family:sans-serif;margin:0}}
            header{{padding:25px 5%;border-bottom:6px solid #fff;display:flex;justify-content:space-between;align-items:center}}
            .logo{{display:flex;align-items:center;gap:15px;text-decoration:none;color:#fff;font-size:52px;font-weight:900;font-family:serif;letter-spacing:-3px}}
            .logo img {{ width: 55px; height: 55px; object-fit: contain; }}
            .main{{display:grid;grid-template-columns: 2.2fr 1fr 0.8fr;gap:50px;padding:50px 5%}}
            h1.hero-title {{font-size:65px;line-height:0.9;margin:25px 0;letter-spacing:-4px;font-weight:900}}
        </style></head><body>
        {tv_ticker}
        <header><a href='#' class='logo'><img src='{FAVICON_PATH}'>BrokeNoMore</a><div style='text-align:right;color:#fbbf24;font-weight:900;font-size:14px'>LIVE TERMINAL // 03:00 AM</div></header>
        <div class='main'>
            <div><a href='./{hero['p']}' style='color:#fff;text-decoration:none'><img src='{hero['img']}' style='width:100%;height:520px;object-fit:cover;border:2px solid #333;filter:grayscale(100%)'><h1 class='hero-title'>{hero['t']}</h1></a></div>
            <div style='border-left:1px solid #222;padding-left:40px'><h2 style='color:#fbbf24;font-size:11px;text-transform:uppercase;border-bottom:1px solid #333;padding-bottom:15px;letter-spacing:2px'>Intelligence Grid</h2>{grid_html}</div>
            <div style='border-left:1px solid #222;padding-left:40px'><h2 style='color:#fbbf24;font-size:11px;text-transform:uppercase;border-bottom:1px solid #333;padding-bottom:15px;letter-spacing:2px'>Global Feed</h2><ul>{"".join([f"<li style='margin-bottom:18px;border-bottom:1px solid #111;padding-bottom:10px'><a href='./{a['p']}' style='color:#999;text-decoration:none;font-size:14px;font-weight:bold'>{a['t']}</a></li>" for a in articles[5:]])}</ul></div>
        </div></body></html>""")

if __name__ == "__main__": run()
