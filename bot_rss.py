import feedparser, os, random, time, requests
from datetime import datetime
from bs4 import BeautifulSoup

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def build_pro_article(title, summary):
    # Đoạn nội dung "nhồi" chuyên sâu để tăng độ uy tín và độ dài bài viết
    expert_segments = [
        "The volatility in equity risk premiums is reaching a critical threshold. Our quantitative models suggest a significant liquidity gap in the derivatives market.",
        "Institutional order flow shows heavy accumulation in defensive positions. Traders should watch the VIX closely for any signs of a structural breakout.",
        "From a technical perspective, the 200-day moving average is holding as a primary support level. Fibonacci retracement levels indicate a 61.8% bounce is imminent.",
        "The macro-economic backdrop remains clouded by central bank hawkishness, forcing asset managers to pivot towards high-yield alternatives in the short term."
    ]
    
    analysis = summary
    if GROQ_API_KEY:
        # Prompt ép AI viết dài, dùng thuật ngữ chuyên môn để tăng CPM
        prompt = f"Write a 450-word SENIOR financial analysis on: {title}. Context: {summary}. Tone: Aggressive Wall Street. Structure: 4 long paragraphs."
        try:
            headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
            payload = {"model": "llama3-70b-8192", "messages": [{"role": "user", "content": prompt}], "temperature": 0.5}
            res = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers, timeout=15).json()
            analysis = res['choices'][0]['message']['content'].replace('**', '')
        except: pass

    # Trộn nội dung: AI viết + 2 đoạn expert ngẫu nhiên = Bài viết > 600 chữ
    extra = "\n\n".join(random.sample(expert_segments, 2))
    return f"{analysis}\n\n{extra}\n\n[BNM TERMINAL DATA FEED]: Strategic rebalancing initiated."

def run():
    posts_dir = 'posts'
    if not os.path.exists(posts_dir): os.makedirs(posts_dir)
    articles = []
    v = int(time.time())
    
    # Gom tin từ 4 nguồn RSS lớn nhất của CNBC
    sources = [
        'https://www.cnbc.com/id/10000667/device/rss/rss.html',
        'https://www.cnbc.com/id/100003114/device/rss/rss.html',
        'https://www.cnbc.com/id/19770192/device/rss/rss.html',
        'https://www.cnbc.com/id/20910258/device/rss/rss.html'
    ]
    
    # Danh sách ID ảnh tài chính xịn trên Unsplash để thay đổi liên tục
    finance_ids = [
        '1611974717482-58a252c85aec', '1590283603385-17ffb3a7f29f', 
        '1611606063040-3f047a45686a', '1526303306684-21d1b95703ea', 
        '1535320903710-d9c526a63d56', '1460306423983-3db442003221'
    ]
    
    for url in sources:
        feed = feedparser.parse(url)
        for e in feed.entries[:8]:
            # Mỗi bài báo bốc 1 ảnh ngẫu nhiên từ list ID trên
            selected_id = random.choice(finance_ids)
            img = f"https://images.unsplash.com/photo-{selected_id}?auto=format&fit=crop&w=800&q=80&sig={random.randint(1,99999)}"
            
            summary_raw = BeautifulSoup(e.summary, 'html.parser').get_text()
            content = build_pro_article(e.title, summary_raw)
            
            fname = f"{datetime.now().strftime('%H%M%S')}-{random.randint(100,999)}.html"
            path = os.path.join(posts_dir, fname)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(f"<html><head><meta charset='UTF-8'><title>{e.title}</title><style>body{{font-family:sans-serif;max-width:850px;margin:0 auto;padding:60px 20px;line-height:1.8;font-size:19px;color:#1a1a1a}}img{{width:100%;border-radius:4px;margin-bottom:30px}}h1{{font-size:45px;letter-spacing:-2px;line-height:1.1}}</style></head><body><a href='../index.html' style='color:#666;text-decoration:none'>← TERMINAL HOME</a><h1>{e.title}</h1><img src='{img}'><p style='white-space:pre-wrap'>{content}</p></body></html>")
            articles.append({'t': e.title, 'p': path, 'img': img})

    # Render Index: Giao diện List dài dằng dặc cho bot click quét link
    grid_items = "".join([f"<div style='border-bottom:1px solid #eee;padding:25px 0;display:grid;grid-template-columns:220px 1fr;gap:25px;'><img src='{a['img']}' style='width:220px;height:130px;object-fit:cover;border-radius:4px;'><div><h2 style='font-size:20px;margin:0;line-height:1.2'><a href='{a['p']}?v={v}' style='color:#000;text-decoration:none;'>{a['t']}</a></h2><p style='color:#666;font-size:15px;margin:10px 0;'>Institutional intelligence feed. Market liquidity analysis for professional traders.</p></div></div>" for a in articles])

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(f"""<!DOCTYPE html><html><head><meta charset='UTF-8'><title>BNM Terminal - Institutional Feed</title><style>body{{font-family:sans-serif;margin:0;padding:0;background:#fff}}header{{background:#000;color:#fff;padding:25px 5%;display:flex;justify-content:space-between;align-items:center}}.logo{{font-size:35px;font-weight:900;letter-spacing:-3px;text-transform:uppercase}}.container{{max-width:1100px;margin:40px auto;padding:0 20px}}</style></head><body><header><div class='logo'>BrokeNoMore</div><div style='font-size:12px;font-weight:900;color:#0f0'>● LIVE DATA TERMINAL</div></header><div class='container'>{grid_items}</div></body></html>""")

if __name__ == "__main__": run()
