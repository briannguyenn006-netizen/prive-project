import feedparser, os, random, time, requests
from datetime import datetime
from bs4 import BeautifulSoup

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def build_pro_article(title, summary):
    analysis = summary
    if GROQ_API_KEY:
        prompt = f"Financial analysis: {title}. Context: {summary}. Professional tone."
        try:
            headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
            payload = {"model": "llama3-70b-8192", "messages": [{"role": "user", "content": prompt}], "temperature": 0.6}
            res = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers, timeout=15).json()
            analysis = res['choices'][0]['message']['content'].replace('**', '').strip()
        except: pass
    return f"{analysis}\n\n[TERMINAL]: Strategic update confirmed."

def run():
    # Gom hết vào posts cho sạch nhà
    posts_dir = 'posts'
    if not os.path.exists(posts_dir): os.makedirs(posts_dir)
    
    # Xóa bớt file cũ trong folder posts trước khi tạo mới (để tránh đầy dung lượng)
    for f in os.listdir(posts_dir): os.remove(os.path.join(posts_dir, f))

    articles = []
    v = int(time.time())
    sources = ['https://www.cnbc.com/id/10000667/device/rss/rss.html']
    fav_url = "https://cdn-icons-png.flaticon.com/512/2533/2533512.png"

    for url in sources:
        feed = feedparser.parse(url)
        for e in feed.entries[:8]:
            img = f"https://images.unsplash.com/photo-1611974714658-058e132215bd?w=800&sig={random.randint(1,999)}"
            content = build_pro_article(e.title, e.summary)
            fname = f"news-{random.randint(1000,9999)}.html"
            path = os.path.join(posts_dir, fname)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(f"<html><head><meta charset='UTF-8'><link rel='icon' href='{fav_url}'><title>{e.title}</title><style>body{{font-family:serif;max-width:800px;margin:0 auto;padding:50px;line-height:2}}img{{width:100%;filter:grayscale(100%)}}</style></head><body><a href='../index.html?v={v}'>← BACK</a><h1>{e.title}</h1><img src='{img}'><p>{content}</p></body></html>")
            articles.append({'t': e.title, 'p': path, 'img': img})

    # Render index.html
    items = "".join([f"<div style='border-bottom:2px solid #000;padding:20px;'><a href='./{a['p']}?v={v}' style='color:#000;text-decoration:none;'><img src='{a['img']}' style='width:100px;float:left;margin-right:20px;filter:grayscale(100%)'><h3>{a['t']}</h3></a><div style='clear:both'></div></div>" for a in articles])
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(f"<!DOCTYPE html><html><head><meta charset='UTF-8'><link rel='icon' href='{fav_url}'><title>BROKENOMORE</title></head><body><header style='padding:40px;border-bottom:10px solid #000;'><h1 style='font-size:70px;letter-spacing:-6px;'>BROKENOMORE</h1></header><div style='max-width:1200px;margin:auto;'>{items}</div></body></html>")

if __name__ == "__main__": run()
