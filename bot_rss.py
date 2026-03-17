import feedparser, os, random, time, google.generativeai as genai
from datetime import datetime
from bs4 import BeautifulSoup

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

RSS_SOURCES = {
    'Markets': 'https://www.cnbc.com/id/10000667/device/rss/rss.html',
    'Finance': 'https://www.cnbc.com/id/100003114/device/rss/rss.html'
}

def get_relevant_image(title):
    # Lấy 2 từ quan trọng nhất trong tiêu đề để tìm ảnh liên quan
    words = [w for w in title.split() if len(w) > 3]
    query = "+".join(words[:2]) if words else "finance"
    return f"https://source.unsplash.com/featured/800x500?{query}"

def analyze_news(title, raw_context):
    if not GOOGLE_API_KEY: return raw_context
    prompt = f"Write a 450-word financial analysis for: {title}. Context: {raw_context}. No bold. Use 4 long paragraphs."
    try:
        res = model.generate_content(prompt)
        # Nếu AI viết quá ngắn, tui ép nó lấy nội dung từ một prompt khác hoặc trả về lỗi có ý nghĩa
        return res.text.replace('**', '').strip() if len(res.text) > 800 else f"{raw_context}\n\n[Analysis expanding...]"
    except: return raw_context

def run():
    posts_dir = 'posts'
    if not os.path.exists(posts_dir): os.makedirs(posts_dir)
    articles = []
    v = int(time.time())

    for _, url in RSS_SOURCES.items():
        f = feedparser.parse(url)
        for e in f.entries[:4]:
            img = get_relevant_image(e.title)
            summary = BeautifulSoup(e.summary, 'html.parser').get_text()
            content = analyze_news(e.title, summary)
            
            fname = f"{datetime.now().strftime('%H%M%S')}-{random.randint(10,99)}.html"
            path = os.path.join(posts_dir, fname)
            
            with open(path, 'w', encoding='utf-8') as f_out:
                f_out.write(f"<html><head><meta charset='UTF-8'><link rel='icon' href='../favicon.png?v={v}'><link href='https://fonts.googleapis.com/css2?family=Inter:wght@400;900&display=swap' rel='stylesheet'><style>body{{font-family:Inter;max-width:800px;margin:0 auto;padding:50px 20px;line-height:1.9}}h1{{font-size:45px;letter-spacing:-2px;line-height:1.1}}img{{width:100%;margin:30px 0;border-radius:4px}}</style></head><body><a href='../index.html?v={v}' style='text-decoration:none;color:#000;font-weight:900'>← BACK</a><h1>{e.title}</h1><img src='{img}'><div style='white-space:pre-wrap;font-size:19px'>{content}</div></body></html>")
            articles.append({'t': e.title, 'p': path, 's': content[:200], 'img': img, 'time': datetime.now().strftime('%H:%M')})

    # Render Index
    hero = articles[0]
    latest = "".join([f"<div style='margin-bottom:20px;border-bottom:1px solid #eee;padding-bottom:15px;'><span style='color:red;font-size:11px;font-weight:900'>{a['time']}</span><br><a href='{a['p']}?v={v}' style='color:#000;text-decoration:none;font-weight:700'>{a['t']}</a></div>" for a in articles[1:10]])
    grid = "".join([f"<div><img src='{a['img']}' style='width:100%;height:220px;object-fit:cover;'><h3 style='font-size:20px;font-weight:900;'><a href='{a['p']}?v={v}' style='color:#000;text-decoration:none;'>{a['t']}</a></h3><p style='font-size:14px;color:#666;'>{a['s']}...</p></div>" for a in articles[5:]])

    with open('index.html', 'w', encoding='utf-8') as f_idx:
        f_idx.write(f"""
        <!DOCTYPE html><html><head><meta charset='UTF-8'><title>BrokeNoMore</title><link rel='icon' href='favicon.png?v={v}'><link href='https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap' rel='stylesheet'><style>body{{font-family:Inter;margin:0}}header{{padding:25px 5%;border-bottom:8px solid #000}}.logo{{font-size:40px;font-weight:900;text-decoration:none;color:#000;letter-spacing:-2px}}.container{{max-width:1300px;margin:40px auto;padding:0 20px;display:grid;grid-template-columns:2.5fr 1fr;gap:50px}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:30px;margin-top:40px;border-top:5px solid #000;padding-top:30px}}</style></head>
        <body><header><a href='/' class='logo'>BrokeNoMore</a></header>
        <div style='background:#000;padding:10px 0'><script type='text/javascript' src='https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js' async>{{ "symbols": [{{"proName": "OANDA:XAUUSD", "title": "GOLD"}}, {{"proName": "BITSTAMP:BTCUSD", "title": "BTC"}}]}}</script></div>
        <div class='container'>
            <div><img src='{hero['img']}' style='width:100%;height:500px;object-fit:cover;'><h1 style='font-size:50px;font-weight:900;line-height:1;margin:25px 0'><a href='{hero['p']}?v={v}' style='color:#000;text-decoration:none;'>{hero['t']}</a></h1><p style='font-size:20px;color:#333'>{hero['s']}...</p><div class='grid'>{grid}</div></div>
            <div style='border-left:3px solid #000;padding-left:30px'><h3 style='text-transform:uppercase;border-bottom:6px solid #000;padding-bottom:10px;margin-bottom:25px;font-weight:900'>Latest</h3>{latest}</div>
        </div></body></html>""")

if __name__ == "__main__": run()
