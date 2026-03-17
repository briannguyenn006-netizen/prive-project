import feedparser, os, random, time, google.generativeai as genai
from datetime import datetime
from bs4 import BeautifulSoup

# ==========================================
# CẤU HÌNH AN TOÀN & BẢN QUYỀN
# ==========================================
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

RSS_SOURCES = {
    'Global_Markets': 'https://www.cnbc.com/id/10000667/device/rss/rss.html',
    'Finance_Intelligence': 'https://www.cnbc.com/id/100003114/device/rss/rss.html',
    'Strategy': 'http://feeds.reuters.com/reuters/businessNews'
}

def rewrite_and_transform(title, summary):
    if not GOOGLE_API_KEY: return "Data stream encrypted. Key required."
    
    # Prompt ép AI viết lại hoàn toàn để tránh bản quyền
    prompt = f"""
    REWRITE THIS NEWS COMPLETELY. DO NOT COPY ANY SENTENCE.
    Source Title: {title}
    Source Context: {summary}
    
    TASK: Write a 450-word deep-dive report in professional financial English.
    STRUCTURE:
    - Market Sentiment (2 long paragraphs)
    - Institutional Impact (2 long paragraphs)
    - Strategic Outlook for BNM Clients (1 long paragraph)
    
    STRICT RULES:
    1. Tone: Cold, institutional, like a Bloomberg Terminal.
    2. Words: Minimum 400 words.
    3. Copyright: Use NO phrases from the source.
    4. Formatting: NO bold (**). NO bullet points.
    """
    
    max_retries = 3
    for i in range(max_retries):
        try:
            res = model.generate_content(prompt)
            output = res.text.replace('**', '').strip()
            # Nếu bài đủ dài (>1500 ký tự) thì mới lấy
            if len(output) > 1500:
                return output
            time.sleep(1) # Chờ xíu để tránh spam API
        except:
            continue
    return "The BNM Intelligence desk is currently processing this high-volatility event. Full report arriving in the next terminal sync."

def run_terminal():
    posts_dir = 'posts'
    if not os.path.exists(posts_dir): os.makedirs(posts_dir)
    articles = []
    v_id = int(time.time())

    # Quét tin và xử lý
    for _, url in RSS_SOURCES.items():
        feed = feedparser.parse(url)
        for entry in feed.entries[:5]: # Lấy 15 tin tổng
            # Lấy ảnh Stock chất lượng cao (Tránh lấy ảnh gốc bị dính bản quyền + lỗi hiển thị)
            img_id = random.randint(1, 1000)
            thumb = f"https://picsum.photos/seed/{img_id}/800/500"
            
            clean_summary = BeautifulSoup(entry.summary, 'html.parser').get_text()
            # AI thực hiện "xào nấu" tin
            ai_content = rewrite_and_transform(entry.title, clean_summary)
            
            # Tạo file bài viết
            f_slug = "".join(x for x in entry.title if x.isalnum())[:15]
            filename = f"{datetime.now().strftime('%H%M%S')}-{f_slug}.html"
            filepath = os.path.join(posts_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"""
                <html><head><meta charset='UTF-8'><title>{entry.title} | BNM</title>
                <link href='https://fonts.googleapis.com/css2?family=Inter:wght@400;900&display=swap' rel='stylesheet'>
                <style>body{{font-family:'Inter';max-width:850px;margin:0 auto;padding:60px 20px;line-height:1.9;color:#111}}h1{{font-size:50px;font-weight:900;letter-spacing:-3px;line-height:1}}img{{width:100%;border-radius:4px;margin:30px 0}}.content{{white-space:pre-wrap;font-size:20px;text-align:justify}}</style></head>
                <body><a href='../index.html?v={v_id}' style='font-weight:900;text-decoration:none;color:#000'>← TERMINAL</a><h1>{entry.title}</h1><img src='{thumb}'><div class='content'>{ai_content}</div></body></html>
                """)
            articles.append({'t': entry.title, 'p': filepath, 's': ai_content[:250], 'img': thumb})

    # Render Index.html - LAYOUT GRID TỰ ĐỘNG
    hero = articles[0]
    grid_items = "".join([f"""
    <div style='margin-bottom:50px; border-bottom:1px solid #eee; padding-bottom:30px;'>
        <img src='{a['img']}' style='width:100%; height:250px; object-fit:cover; border-radius:4px;'>
        <h3 style='font-size:24px; margin:15px 0;'><a href='{a['p']}?v={v_id}' style='color:#000; text-decoration:none; font-weight:900;'>{a['t']}</a></h3>
        <p style='color:#555; font-size:16px;'>{a['s']}...</p>
    </div>""" for a in articles[1:]])

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(f"""
        <!DOCTYPE html><html><head><meta charset='UTF-8'><title>BNM Terminal</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Inter', sans-serif; margin: 0; background: #fff; }}
            header {{ padding: 30px; border-bottom: 8px solid #000; text-align: center; }}
            .logo {{ font-size: 50px; font-weight: 900; text-transform: uppercase; color: #000; text-decoration: none; letter-spacing: -4px; }}
            .container {{ max-width: 1400px; margin: 50px auto; padding: 0 20px; display: grid; grid-template-columns: 2.5fr 1fr; gap: 60px; }}
            .news-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 40px; margin-top: 50px; border-top: 8px solid #000; padding-top: 40px; }}
        </style></head>
        <body><header><a href='/' class='logo'>BrokeNoMore</a></header>
        <div style='background:#000; padding:12px 0;'><script type='text/javascript' src='https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js' async>{{ "symbols": [{{"proName": "OANDA:XAUUSD", "title": "GOLD"}}, {{"proName": "BITSTAMP:BTCUSD", "title": "BTC"}}]}}</script></div>
        <div class='container'>
            <div>
                <img src='{hero['img']}' style='width:100%; height:600px; object-fit:cover;'>
                <h1 style='font-size:60px; font-weight:900; letter-spacing:-3px; margin:30px 0; line-height:1;'><a href='{hero['p']}?v={v_id}' style='color:#000; text-decoration:none;'>{hero['t']}</a></h1>
                <p style='font-size:24px; color:#333;'>{hero['s']}...</p>
                <div class='news-grid'>{grid_items}</div>
            </div>
            <div style='border-left: 2px solid #000; padding-left: 40px;'>
                <h3 style='font-size:14px; text-transform:uppercase; border-bottom:8px solid #000; padding-bottom:10px; margin-bottom:30px; font-weight:900;'>Intelligence Stream</h3>
                {grid_items[:2000]} </div>
        </div></body></html>
        """)

if __name__ == "__main__":
    run_terminal()
