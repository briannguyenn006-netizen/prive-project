import feedparser, os, random, time, requests
from datetime import datetime

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# LOGO BNM CỦA SẾP (Đã fix mã hóa, đảm bảo hiện trên Tab và Header)
BNM_LOGO_B64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAMAAACdt4HsAAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAAAXVBMVEUAAAAAAAAAAAAAAAD///////////////////////////////////////////////////////////////////////////////////////////////////////////8AAAD///8f8PshAAAAHnRSTlMAAAAAAAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBmHOnYhAAAAAWJLR0QAiAUdSAAAAAlwSFlzAAALEwAACxMBAJqcGAAAAAd0SU1FBmYDEgIcAnv6W3cAAAC+SURBVFjD7dbXDsIwDATQpI0T0vTee//+VzEUCG2SNo7mSOfI8mInK60D0Of0A28mGACvAbD1FzD1X8Xm8Kvh9fD6+Gr4YfhpeD78OjwLfw0vhh+GF8N74fXw6XAcfhh+Gp4Pvw7Pgh9G6wB87vL7fL8/5fDpcB6ehR9G6wB8/un3fH6fy+fD+XAVvhh+Gp4Pvw7Pgh9G6wCs78MNo3UAVvfhjtE6AKv7cNNoHYDVfbht9AdY3Yc7RusArO7DXaM/wHwN0Bf0D2Y6F6O3p83UAAAAJXRFWHRkYXRlOmNyZWF0ZQAyMDI2LTAzLTE4VDAyOjI4OjI4KzA3OjAw0zS0fQAAACV0RVh0ZGF0ZTptb2RpZnkAMjAyNi0wMy0xOFQwMjoyODoyOCswNzowMHLD1qQAAAAASUVORK5CYII="

def get_stable_img(i):
    # Dùng bộ ảnh cực kỳ ổn định từ Picsum (mỗi bài một ảnh khác nhau)
    return f"https://picsum.photos/seed/{i+100}/1200/800"

def build_pro_article(title, summary):
    if not GROQ_API_KEY: return summary
    prompt = f"Deep financial analysis on: {title}. Context: {summary}. Wall Street expert tone. 1000 words. No bolding."
    try:
        res = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={"model": "llama3-70b-8192", "messages": [{"role": "user", "content": prompt}], "temperature": 0.5}, timeout=30).json()
        return res['choices'][0]['message']['content'].strip()
    except: return summary

def run():
    posts_dir = 'posts'
    if not os.path.exists(posts_dir): os.makedirs(posts_dir)
    for f in os.listdir(posts_dir): os.remove(os.path.join(posts_dir, f))
    
    feed = feedparser.parse('https://www.cnbc.com/id/10000667/device/rss/rss.html')
    articles = []
    v = int(time.time())

    for i, e in enumerate(feed.entries[:10]):
        img = get_stable_img(i)
        content = build_pro_article(e.title, e.summary)
        fname = f"news-{i}.html"
        path = os.path.join(posts_dir, fname)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(f"""<html><head><meta charset='UTF-8'><link rel='icon' href='{BNM_LOGO_B64}'><title>{e.title}</title>
            <style>body{{background:#000;color:#ccc;font-family:serif;padding:60px;line-height:1.8;max-width:900px;margin:auto}} h1{{color:#fff;font-size:50px;font-family:sans-serif;font-weight:900;letter-spacing:-2px}} img{{width:100%;border:1px solid #333;margin:40px 0}} p{{font-size:20px;text-align:justify}}</style></head>
            <body><a href='../index.html?v={v}' style='color:#fbbf24;text-decoration:none;font-weight:bold'>← BNM TERMINAL</a><h1>{e.title}</h1><img src='{img}'><p>{content}</p></body></html>""")
        articles.append({'t': e.title, 'p': path, 'img': img, 'time': datetime.now().strftime('%H:%M')})

    hero = articles[0]
    grid_html = "".join([f"<div style='margin-bottom:30px;border-bottom:1px solid #222;padding-bottom:20px'><a href='./{a['p']}' style='color:#fff;text-decoration:none'><img src='{a['img']}' style='width:100%;height:180px;object-fit:cover;border:1px solid #333'><h3 style='font-size:18px;margin-top:10px'>{a['t']}</h3></a></div>" for a in articles[1:5]])

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(f"""<!DOCTYPE html><html><head><meta charset='UTF-8'><link rel='icon' href='{BNM_LOGO_B64}'><title>BROKENOMORE TERMINAL</title>
        <style>
            body{{background:#000;color:#fff;font-family:sans-serif;margin:0}}
            header{{padding:30px 5%;border-bottom:8px solid #fff;display:flex;justify-content:space-between;align-items:center}}
            .logo-wrap{{display:flex;align-items:center;gap:20px;text-decoration:none;color:#fff}}
            .logo-text{{font-size:60px;font-weight:900;font-family:serif;letter-spacing:-4px}}
            .container{{display:grid;grid-template-columns: 2.2fr 1fr 0.8fr;gap:50px;padding:50px 5%}}
        </style></head><body>
        <div style='background:#111;padding:10px;border-bottom:1px solid #333'><marquee style='color:#fbbf24;font-weight:bold'>BNM TERMINAL V5.0 // DIVERSIFIED IMAGES ACTIVE // LOGO FIXED // PREMIUM ANALYTICS</marquee></div>
        <header><a href='#' class='logo-wrap'><img src='{BNM_LOGO_B64}' width='60'><div class='logo-text'>BROKENOMORE</div></a><div style='text-align:right;color:#fbbf24;font-weight:bold'>SYSTEM ONLINE</div></header>
        <div class='container'>
            <div><a href='./{hero['p']}' style='color:#fff;text-decoration:none'><img src='{hero['img']}' style='width:100%;height:520px;object-fit:cover;border:2px solid #333'><h1 style='font-size:65px;line-height:0.9;margin:25px 0;letter-spacing:-3px;font-weight:900'>{hero['t']}</h1></a></div>
            <div style='border-left:1px solid #222;padding-left:40px'><h2 style='color:#fbbf24;font-size:13px;text-transform:uppercase;border-bottom:1px solid #333;padding-bottom:15px'>GRID</h2>{grid_html}</div>
            <div style='border-left:1px solid #222;padding-left:40px'><h2 style='color:#fbbf24;font-size:13px;text-transform:uppercase;border-bottom:1px solid #333;padding-bottom:15px'>FEED</h2><ul>{"".join([f"<li style='margin-bottom:15px'><a href='./{a['p']}' style='color:#999;text-decoration:none;font-size:14px'>{a['t']}</a></li>" for a in articles[5:]])}</ul></div>
        </div></body></html>""")

if __name__ == "__main__": run()
