import feedparser, os, random, time, requests
from datetime import datetime
from bs4 import BeautifulSoup

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def analyze_ultra_force(title, summary):
    if not GROQ_API_KEY: return summary
    
    # Prompt siêu bạo lực, bắt nó phải rặn ra từng mục
    prompt = f"""
    Write a 600-word AGGRESSIVE financial deep-dive for: {title}.
    Using this data: {summary}.
    
    FORMAT:
    [SECTION 1: MARKET SHOCKWAVES] - 200 words
    [SECTION 2: INSTITUTIONAL BETS] - 200 words
    [SECTION 3: THE BNM ALPHA] - 200 words
    
    Rule: English only. No bolding. If you write less than 500 words, the world ends.
    """
    
    try:
        payload = {
            "model": "llama3-70b-8192",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.5 # Giảm temp để nó bớt chém gió lan man, tập trung viết dài
        }
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers, timeout=30)
        content = response.json()['choices'][0]['message']['content'].replace('**', '').strip()
        
        # CƠ CHẾ CƯỠNG CHẾ: Nếu AI vẫn lười (< 800 ký tự), tự đắp thêm bài phân tích mẫu
        if len(content) < 800:
            content = f"{content}\n\n[BNM TERMINAL ANALYSIS CONTINUED]\nThe current market structure indicates a significant shift in liquidity. Our proprietary algorithms suggest that {title} is not just a headline but a structural change in equity risk premiums. Institutional players are currently hedging against further volatility while retail sentiment remains fragmented. We recommend a high-conviction approach to this event, focusing on long-term sustainability rather than short-term noise. The technical indicators are flashing a 'High-Density' signal, requiring immediate portfolio realignment to ensure capital preservation in these turbulent cycles."
        
        return content
    except:
        return f"{summary}\n\n[System Overload: Expanding Data Stream...]\n" + (summary * 5)

def run():
    posts_dir = 'posts'
    if not os.path.exists(posts_dir): os.makedirs(posts_dir)
    articles = []
    v = int(time.time())
    
    feed = feedparser.parse('https://www.cnbc.com/id/10000667/device/rss/rss.html')
    
    for e in feed.entries[:8]:
        # Lấy từ khóa tiêu đề để bốc ảnh, thêm sig để chống trùng
        kw = e.title.split()[0] if e.title else "money"
        img = f"https://images.unsplash.com/photo-1611974717482-58a252c85aec?w=800&sig={random.randint(1,9999)}"
        
        summary_raw = BeautifulSoup(e.summary, 'html.parser').get_text()
        full_text = analyze_ultra_force(e.title, summary_raw)
        
        fname = f"{datetime.now().strftime('%H%M%S')}-{random.randint(10,99)}.html"
        path = os.path.join(posts_dir, fname)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(f"<html><head><meta charset='UTF-8'><link rel='icon' href='../favicon.png?v={v}'><link href='https://fonts.googleapis.com/css2?family=Inter:wght@400;900&display=swap' rel='stylesheet'><style>body{{font-family:Inter;max-width:800px;margin:0 auto;padding:60px 20px;line-height:1.8;color:#111}}h1{{font-size:45px;font-weight:900;letter-spacing:-3px;line-height:1}}img{{width:100%;margin:30px 0;border-radius:4px;box-shadow:0 10px 30px rgba(0,0,0,0.1)}}p{{font-size:19px;text-align:justify;white-space:pre-wrap}}</style></head><body><a href='../index.html?v={v}' style='text-decoration:none;color:#000;font-weight:900'>← BACK TO TERMINAL</a><h1>{e.title}</h1><img src='{img}'><p>{full_text}</p></body></html>")
        articles.append({'t': e.title, 'p': path, 's': full_text[:250], 'img': img, 'time': datetime.now().strftime('%H:%M')})

    # Render Index
    hero = articles[0]
    side = "".join([f"<div style='margin-bottom:25px;border-bottom:1px solid #eee;padding-bottom:15px;'><span style='color:red;font-size:11px;font-weight:900;'>{a['time']}</span><br><a href='{a['p']}?v={v}' style='color:#000;text-decoration:none;font-weight:700;'>{a['t']}</a></div>" for a in articles[1:10]])
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(f"<!DOCTYPE html><html><head><meta charset='UTF-8'><title>BrokeNoMore</title><link rel='icon' href='favicon.png?v={v}'><link href='https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap' rel='stylesheet'><style>body{{font-family:Inter;margin:0}}header{{padding:30px 5%;border-bottom:8px solid #000}}.logo{{font-size:45px;font-weight:900;text-decoration:none;color:#000;letter-spacing:-3px;text-transform:uppercase}}.container{{max-width:1300px;margin:40px auto;padding:0 20px;display:grid;grid-template-columns:2.5fr 1fr;gap:50px}}</style></head><body><header><a href='/' class='logo'>BrokeNoMore</a></header><div class='container'><div><img src='{hero['img']}' style='width:100%;height:500px;object-fit:cover;'><h1><a href='{hero['p']}?v={v}' style='color:#000;text-decoration:none;'>{hero['t']}</a></h1><p style='font-size:20px'>{hero['s']}...</p></div><div style='border-left:3px solid #000;padding-left:30px'><h3 style='font-size:14px;text-transform:uppercase;border-bottom:6px solid #000;padding-bottom:10px;margin-bottom:25px;font-weight:900'>Latest</h3>{side}</div></div></body></html>")

if __name__ == "__main__": run()
