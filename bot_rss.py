import feedparser, os, random, time, requests
from datetime import datetime
from bs4 import BeautifulSoup

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# LOGO BNM CỦA SẾP (Mã hóa Base64)
FAVICON_DATA = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAMAAACdt4HsAAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAAAXVBMVEUAAAAAAAAAAAAAAAD///////////////////////////////////////////////////////////////////////////////////////////////////////////8AAAD///8f8PshAAAAHnRSTlMAAAAAAAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBmHOnYhAAAAAWJLR0QAiAUdSAAAAAlwSFlzAAALEwAACxMBAJqcGAAAAAd0SU1FBmYDEgIcAnv6W3cAAAC+SURBVFjD7dbXDsIwDATQpI0T0vTee//+VzEUCG2SNo7mSOfI8mInK60D0Of0A28mGACvAbD1FzD1X8Xm8Kvh9fD6+Gr4YfhpeD78OjwLfw0vhh+GF8N74fXw6XAcfhh+Gp4Pvw7Pgh9G6wB87vL7fL8/5fDpcB6ehR9G6wB8/un3fH6fy+fD+XAVvhh+Gp4Pvw7Pgh9G6wCs78MNo3UAVvfhjtE6AKv7cNNoHYDVfbht9AdY3Yc7RusArO7DXaM/wHwN0Bf0D2Y6F6O3p83UAAAAJXRFWHRkYXRlOmNyZWF0ZQAyMDI2LTAzLTE4VDAyOjI4OjI4KzA3OjAw0zS0fQAAACV0RVh0ZGF0ZTptb2RpZnkAMjAyNi0wMy0xOFQwMjoyODoyOCswNzowMHLD1qQAAAAASUVORK5CYII="

def build_pro_article(title, summary):
    analysis = summary
    if GROQ_API_KEY:
        # TỰ GIÁC: Nâng cấp Prompt để bài viết dài và chi tiết hơn
        prompt = f"""Write a comprehensive financial analysis report (at least 600 words) for the headline: "{title}".
        Context: {summary}
        Requirements:
        1. Use professional Wall Street terminology.
        2. Structure: Market Overview, Technical Breakdown, Institutional Sentiment, and Forward Outlook.
        3. Do not use bold markers (**). 
        4. Focus on macroeconomic impact and liquidity flows.
        Make it look like a premium Bloomberg Terminal report."""
        
        try:
            headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
            payload = {"model": "llama3-70b-8192", "messages": [{"role": "user", "content": prompt}], "temperature": 0.6}
            res = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers, timeout=20).json()
            analysis = res['choices'][0]['message']['content'].strip()
        except: pass
    return analysis

def run():
    posts_dir = 'posts'
    if not os.path.exists(posts_dir): os.makedirs(posts_dir)
    for f in os.listdir(posts_dir): os.remove(os.path.join(posts_dir, f))

    articles = []
    v = int(time.time())
    feed = feedparser.parse('https://www.cnbc.com/id/10000667/device/rss/rss.html')

    for i, e in enumerate(feed.entries[:10]):
        # Mỗi bài 1 ảnh khác nhau hoàn toàn cho uy tín
        img = f"https://images.unsplash.com/photo-{1611974714658 + i}-058e132215bd?w=1000&q=90&fit=crop"
        content = build_pro_article(e.title, e.summary)
        fname = f"news-{random.randint(1000,9999)}.html"
        path = os.path.join(posts_dir, fname)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(f"""<html><head><meta charset='UTF-8'><link rel='icon' href='{FAVICON_DATA}'><title>{e.title} | BROKENOMORE</title>
            <style>
                body{{background:#050505;color:#ddd;font-family:'Times New Roman',serif;margin:0;padding:60px 20px;line-height:1.8}}
                .wrap{{max-width:850px;margin:auto}}
                .brand{{display:flex;align-items:center;gap:12px;color:#fbbf24;text-decoration:none;font-weight:900;letter-spacing:1px;font-family:sans-serif;font-size:14px}}
                h1{{font-size:52px;color:#fff;line-height:1;margin:30px 0;letter-spacing:-2px;font-weight:900}}
                img{{width:100%;border-radius:4px;border:1px solid #333;margin:40px 0}}
                p{{font-size:20px;text-align:justify;white-space:pre-wrap;color:#ccc}}
                .meta{{border-top:1px solid #333;padding-top:20px;margin-top:40px;color:#888;font-size:14px;font-family:sans-serif}}
            </style></head><body><div class='wrap'>
                <a href='../index.html?v={v}' class='brand'><img src='{FAVICON_DATA}' width='25'> BROKENOMORE TERMINAL</a>
                <h1>{e.title}</h1>
                <div style='color:#fbbf24;font-weight:bold;margin-bottom:10px'>BY BNM INTELLIGENCE UNIT</div>
                <img src='{img}'>
                <p>{content}</p>
                <div class='meta'>© 2026 BROKENOMORE TERMINAL. All institutional data is time-delayed.</div>
            </div></body></html>""")
        articles.append({'t': e.title, 'p': path, 'img': img, 'time': datetime.now().strftime('%H:%M'), 'summary': e.summary[:150]})

    hero = articles[0]
    grid = "".join([f"<div style='border-bottom:1px solid #222;padding-bottom:15px;margin-bottom:15px'><a href='./{a['p']}' style='color:#fff;text-decoration:none'><img src='{a['img']}' style='width:100%;height:150px;object-fit:cover;filter:grayscale(80%)'><h3 style='font-size:16px;margin:10px 0;line-height:1.2'>{a['t']}</h3></a></div>" for a in articles[1:5]])
    sidebar = "".join([f"<li style='list-style:none;margin-bottom:15px;border-bottom:1px solid #111;padding-bottom:10px'><span style='color:#fbbf24;font-size:10px'>{a['time']}</span><br><a href='./{a['p']}' style='color:#999;text-decoration:none;font-size:13px;font-weight:bold'>{a['t']}</a></li>" for a in articles[5:]])

    tv_widget = """<div class="tradingview-widget-container" style="background:#111; border-bottom:1px solid #333">
    <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
    { "symbols": [{"proName": "FOREXCOM:SPX500", "title": "S&P 500"},{"proName": "FX_IDC:XAUUSD", "title": "Gold"},{"proName": "BITSTAMP:BTCUSD", "title": "Bitcoin"},{"proName": "FX:EURUSD", "title": "EUR/USD"}], "colorTheme": "dark", "isTransparent": true, "displayMode": "adaptive", "locale": "en" }
    </script></div>"""

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(f"""<!DOCTYPE html><html><head><meta charset='UTF-8'><link rel='icon' href='{FAVICON_DATA}'><title>BROKENOMORE TERMINAL</title>
        <style>
            body{{background:#000;color:#fff;font-family:'Helvetica',sans-serif;margin:0}}
            header{{padding:25px 5%;border-bottom:5px solid #fff;display:flex;justify-content:space-between;align-items:center}}
            .logo-wrap{{display:flex;align-items:center;gap:15px;text-decoration:none;color:#fff}}
            .logo-text{{font-size:55px;font-weight:900;letter-spacing:-5px;font-family:serif}}
            .main-grid{{display:grid;grid-template-columns: 2.2fr 1fr 0.8fr;gap:40px;padding:40px 5%}}
        </style></head><body>
        {tv_widget}
        <header><a href='#' class='logo-wrap'><img src='{FAVICON_DATA}' width='55'><div class='logo-text'>BROKENOMORE</div></a><div style='text-align:right;color:#fbbf24;font-weight:bold'>SYSTEM STATUS: OPTIMAL</div></header>
        <div class='main-grid'>
            <div style='border-right:1px solid #222;padding-right:30px'>
                <a href='./{hero['p']}' style='text-decoration:none;color:#fff'><img src='{hero['img']}' style='width:100%;height:480px;object-fit:cover;margin-bottom:25px;'><h1 style='font-size:60px;line-height:0.9;margin:0;letter-spacing:-3px;font-weight:900'>{hero['t']}</h1></a>
                <p style='color:#888;font-size:20px;margin-top:20px;line-height:1.5'>{hero['summary']}... [CONTINUE READING]</p>
            </div>
            <div style='border-right:1px solid #222;padding-right:30px'><h2 style='color:#fbbf24;font-size:12px;text-transform:uppercase;border-bottom:1px solid #333;padding-bottom:10px'>Intelligence Grid</h2>{grid}</div>
            <div><h2 style='color:#fbbf24;font-size:12px;text-transform:uppercase;border-bottom:1px solid #333;padding-bottom:10px'>Live Feed</h2><ul style='padding:0;margin:0'>{sidebar}</ul></div>
        </div>
        <div style='position:fixed;bottom:0;width:100%;background:#fbbf24;color:#000;padding:8px;font-weight:900;font-size:12px;z-index:9999'><marquee>BROKENOMORE TERMINAL V3.0 | DEEP ANALYSIS ENABLED | NO REPETITION MODE | TRADINGVIEW SYNCED</marquee></div>
        </body></html>""")

if __name__ == "__main__": run()
