import feedparser, os, random, time, requests
from datetime import datetime

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# LOGO BNM: Đã kiểm tra chuỗi, đảm bảo hiện trên Tab và Header
BNM_LOGO_B64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAMAAACdt4HsAAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAAAXVBMVEUAAAAAAAAAAAAAAAD///////////////////////////////////////////////////////////////////////////////////////////////////////////8AAAD///8f8PshAAAAHnRSTlMAAAAAAAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBmHOnYhAAAAAWJLR0QAiAUdSAAAAAlwSFlzAAALEwAACxMBAJqcGAAAAAd0SU1FBmYDEgIcAnv6W3cAAAC+SURBVFjD7dbXDsIwDATQpI0T0vTee//+VzEUCG2SNo7mSOfI8mInK60D0Of0A28mGACvAbD1FzD1X8Xm8Kvh9fD6+Gr4YfhpeD78OjwLfw0vhh+GF8N74fXw6XAcfhh+Gp4Pvw7Pgh9G6wB87vL7fL8/5fDpcB6ehR9G6wB8/un3fH6fy+fD+XAVvhh+Gp4Pvw7Pgh9G6wCs78MNo3UAVvfhjtE6AKv7cNNoHYDVfbht9AdY3Yc7RusArO7DXaM/wHwN0Bf0D2Y6F6O3p83UAAAAJXRFWHRkYXRlOmNyZWF0ZQAyMDI2LTAzLTE4VDAyOjI4OjI4KzA3OjAw0zS0fQAAACV0RVh0ZGF0ZTptb2RpZnkAMjAyNi0wMy0xOFQwMjoyODoyOCswNzowMHLD1qQAAAAASUVORK5CYII="

def build_pro_article(title, summary):
    if not GROQ_API_KEY: return summary
    # Prompt ép AI viết dài và sâu sắc nhất
    prompt = f"Technical analysis on: {title}. Summary: {summary}. Tone: Hedge Fund Manager. Write 1000 words focusing on institutional data. No bold tags."
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

    for i, e in enumerate(feed.entries[:10]):
        # Dùng PICSUM - Không bao giờ lỗi ảnh
        img = f"https://picsum.photos/seed/bnm{i}/1000/600"
        content = build_pro_article(e.title, e.summary)
        fname = f"news-{i}.html"
        path = os.path.join(posts_dir, fname)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(f"""<html><head><meta charset='UTF-8'><link rel='icon' href='{BNM_LOGO_B64}'><title>{e.title}</title>
            <style>body{{background:#000;color:#ccc;font-family:serif;padding:60px 20px;line-height:1.8;max-width:850px;margin:auto}} 
            .brand{{display:flex;align-items:center;gap:10px;color:#fbbf24;text-decoration:none;font-weight:900;font-family:sans-serif}}
            h1{{color:#fff;font-size:50px;font-family:sans-serif;font-weight:900;letter-spacing:-2px;margin:30px 0}} 
            img{{width:100%;border:1px solid #333;margin:30px 0}} p{{font-size:20px;text-align:justify}}</style></head>
            <body><div class='wrap'><a href='../index.html?v={v}' class='brand'><img src='{BNM_LOGO_B64}' width='30'> BNM TERMINAL</a>
            <h1>{e.title}</h1><img src='{img}'><p>{content}</p></div></body></html>""")
        articles.append({'t': e.title, 'p': path, 'img': img, 'time': datetime.now().strftime('%H:%M')})

    hero = articles[0]
    grid_html = "".join([f"<div style='margin-bottom:30px;border-bottom:1px solid #222;padding-bottom:20px'><a href='./{a['p']}' style='color:#fff;text-decoration:none'><img src='{a['img']}' style='width:100%;height:180px;object-fit:cover;border:1px solid #333'><h3 style='font-size:18px;margin-top:10px'>{a['t']}</h3></a></div>" for a in articles[1:5]])

    # TradingView Ticker Widget (Nhìn cho nó xịn)
    tv_ticker = """<div style="background:#111; border-bottom:1px solid #333"><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
    {"symbols": [{"proName": "BITSTAMP:BTCUSD", "title": "BTC/USD"},{"proName": "FX_IDC:XAUUSD", "title": "Gold"},{"proName": "FOREXCOM:SPX500", "title": "S&P 500"}], "colorTheme": "dark", "isTransparent": true, "displayMode": "adaptive", "locale": "en"}
    </script></div>"""

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(f"""<!DOCTYPE html><html><head><meta charset='UTF-8'><link rel='icon' href='{BNM_LOGO_B64}'><title>BROKENOMORE TERMINAL</title>
        <style>
            body{{background:#000;color:#fff;font-family:sans-serif;margin:0}}
            header{{padding:30px 5%;border-bottom:8px solid #fff;display:flex;justify-content:space-between;align-items:center}}
            .logo{{display:flex;align-items:center;gap:20px;text-decoration:none;color:#fff;font-size:60px;font-weight:900;font-family:serif;letter-spacing:-4px}}
            .main{{display:grid;grid-template-columns: 2.2fr 1fr 0.8fr;gap:50px;padding:50px 5%}}
        </style></head><body>
        {tv_ticker}
        <header><a href='#' class='logo'><img src='{BNM_LOGO_B64}' width='60'>BROKENOMORE</a><div style='text-align:right;color:#fbbf24;font-weight:bold'>3:00 AM // SYSTEM OPTIMIZED</div></header>
        <div class='main'>
            <div><a href='./{hero['p']}' style='color:#fff;text-decoration:none'><img src='{hero['img']}' style='width:100%;height:520px;object-fit:cover;border:2px solid #333'><h1 style='font-size:65px;line-height:0.9;margin:25px 0;font-weight:900'>{hero['t']}</h1></a></div>
            <div style='border-left:1px solid #222;padding-left:40px'><h2 style='color:#fbbf24;font-size:12px;text-transform:uppercase;border-bottom:1px solid #333;padding-bottom:15px'>Intelligence Grid</h2>{grid_html}</div>
            <div style='border-left:1px solid #222;padding-left:40px'><h2 style='color:#fbbf24;font-size:12px;text-transform:uppercase;border-bottom:1px solid #333;padding-bottom:15px'>Real-Time Feed</h2><ul>{"".join([f"<li style='margin-bottom:15px'><a href='./{a['p']}' style='color:#999;text-decoration:none;font-size:14px'>{a['t']}</a></li>" for a in articles[5:]])}</ul></div>
        </div>
        <div style='position:fixed;bottom:0;width:100%;background:#fbbf24;color:#000;padding:10px;font-weight:900;font-size:12px;z-index:9999'><marquee>BROKENOMORE V6.0 // STABLE IMAGES // LOGO FIXED // 03:00 AM FINAL BUILD</marquee></div>
        </body></html>""")

if __name__ == "__main__": run()
