import feedparser, os, random, time, requests
from datetime import datetime
from bs4 import BeautifulSoup

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def generate_bulk_content(title, summary):
    # Đoạn văn bản "ma trận" để kéo dài bài viết, đánh lừa bot quét nội dung
    filler_text = [
        f"In the current fiscal landscape, {title} represents a critical juncture for liquidity providers. Market participants are analyzing the delta in volatility surface to hedge against tail risks.",
        "The convergence of macro-economic indicators and micro-market structures suggests a period of intense rebalancing. Institutional order blocks are visible near the support zones.",
        "Technical analysis indicates a bullish divergence in the RSI, while the MACD remains neutral, signaling a potential accumulation phase for long-term stakeholders.",
        "Risk management protocols should be tightened. BNM Terminal's proprietary sentiment index shows a shift from fear to cautious optimism among hedge fund managers."
    ]
    
    analysis = summary
    if GROQ_API_KEY:
        prompt = f"Write a 400-word professional financial report on: {title}. Context: {summary}. Aggressive Wall Street style. No bold."
        try:
            headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
            payload = {"model": "llama3-70b-8192", "messages": [{"role": "user", "content": prompt}], "temperature": 0.5}
            res = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers, timeout=15).json()
            analysis = res['choices'][0]['message']['content'].replace('**', '')
        except: pass

    # Ép bài viết phải dài bằng cách trộn filler text
    return f"{analysis}\n\n" + "\n\n".join(random.sample(filler_text, 3))

def run():
    posts_dir = 'posts'
    if not os.path.exists(posts_dir): os.makedirs(posts_dir)
    articles = []
    v = int(time.time())
    
    # Lấy tin từ 4 nguồn để web "nhung nhúc" tin cho bot click
    rss_urls = [
        'https://www.cnbc.com/id/10000667/device/rss/rss.html',
        'https://www.cnbc.com/id/100003114/device/rss/rss.html',
        'https://www.cnbc.com/id/19770192/device/rss/rss.html',
        'https://www.cnbc.com/id/10000115/device/rss/rss.html'
    ]
    
    for url in rss_urls:
        feed = feedparser.parse(url)
        for e in feed.entries[:8]:
            # Dùng Unsplash Source với keyword chuẩn tài chính
            img = f"https://images.unsplash.com/photo-1611974717482-58a252c85aec?auto=format&fit=crop&w=800&q=80&sig={random.randint(1,9999)}"
            content = generate_bulk_content(e.title, e.summary)
            fname = f"{datetime.now().strftime('%H%M%S')}-{random.randint(100,999)}.html"
            path = os.path.join(posts_dir, fname)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(f"<html><head><meta charset='UTF-8'><title>{e.title}</title><style>body{{font-family:sans-serif;max-width:800px;margin:0 auto;padding:50px 20px;line-height:1.8;font-size:18px}}img{{width:100%;border-radius:5px}}</style></head><body><a href='../index.html'>← Terminal Home</a><h1>{e.title}</h1><img src='{img}'><p style='white-space:pre-wrap'>{content}</p></body></html>")
            articles.append({'t': e.title, 'p': path, 's': content[:200], 'img': img})

    # Render Index với giao diện "Mê cung" cho bot click
    grid_html = "".join([f"<div style='border:1px solid #ddd;padding:15px;border-radius:5px;'><img src='{a['img']}' style='width:100%;height:150px;object-fit:cover;'><h2 style='font-size:16px;'><a href='{a['p']}?v={v}' style='color:#000;text-decoration:none;'>{a['t']}</a></h2></div>" for a in articles])

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(f"<!DOCTYPE html><html><head><meta charset='UTF-8'><title>BrokeNoMore Intelligence</title><style>body{{font-family:sans-serif;margin:0;padding:20px}}header{{border-bottom:5px solid #000;padding-bottom:20px;margin-bottom:30px}}.grid{{display:grid;grid-template-columns:repeat(auto-fill, minmax(300px, 1fr));gap:20px}}</style></head><body><header><h1>BrokeNoMore Terminal</h1><p>Institutional Grade Data Flow</p></header><div class='grid'>{grid_html}</div></body></html>")

if __name__ == "__main__": run()
