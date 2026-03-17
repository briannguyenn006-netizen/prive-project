import feedparser, os, random, time, requests
from datetime import datetime
from bs4 import BeautifulSoup

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def build_pro_article(title, summary):
    analysis = summary
    if GROQ_API_KEY:
        prompt = f"Financial analysis: {title}. Context: {summary}. Wall Street tone."
        try:
            headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
            payload = {"model": "llama3-70b-8192", "messages": [{"role": "user", "content": prompt}], "temperature": 0.6}
            res = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers, timeout=15).json()
            analysis = res['choices'][0]['message']['content'].replace('**', '').strip()
        except: pass
    return f"{analysis}\n\n[TERMINAL]: Strategic update confirmed."

def run():
    # Gom vào posts cho sạch, tự tạo folder nếu chưa có
    posts_dir = 'posts'
    if not os.path.exists(posts_dir): os.makedirs(posts_dir)
    
    # Xóa sạch bài cũ trong folder posts để không bị rác
    for file in os.listdir(posts_dir):
        os.remove(os.path.join(posts_dir, file))

    articles = []
    v = int(time.time())
    # Favicon lấy icon đồng tiền vàng cho sếp phát tài
    fav_url = "https://cdn-icons-png.flaticon.com/512/2533/2533512.png"

    feed = feedparser.parse('https://www.cnbc.com/id/10000667/device/rss/rss.html')
    for e in feed.entries[:8]:
        # Ảnh Stock tài chính thật
        img = f"https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=800&q=80&sig={random.randint(1,999)}"
        content = build_pro_article(e.title, e.summary)
        fname = f"news-{random.randint(1000,9999)}.html"
        path = os.path.join(posts_dir, fname)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(f"<html><head><meta charset='UTF-8'><link rel='icon' href='{fav_url}'><title>{e.title}</title><style>body{{font-family:serif;max-width:800px;margin:0 auto;padding:50px;line-height:2;background:#fff}}img{{width:100%;filter:grayscale(100%);margin:20px 0;border:1px solid #000}}.back{{text-decoration:none;color:#000;font-weight:bold;border-bottom:2px solid #000}}</style></head><body><a href='../index.html?v={v}' class='back'>← BACK</a><h1>{e.title}</h1><img src='{img}'><p>{content}</p></body></html>")
        articles.append({'t': e.title, 'p': path, 'img': img})

    # Render Index với Logo BROKENOMORE to rõ
    items = "".join([f"<div style='border-bottom:2px solid #000;padding:20px;display:flex;gap:20px;'><img src='{a['img']}' style='width:150px;height:100px;object-fit:cover;filter:grayscale(100%);'><div><a href='./{a['p']}?v={v}' style='color:#000;text-decoration:none;'><h3 style='margin:0;font-size:22px;'>{a['t']}</h3></a></div></div>" for a in articles])
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(f"<!DOCTYPE html><html><head><meta charset='UTF-8'><link rel='icon' href='{fav_url}'><title>BROKENOMORE</title><style>body{{font-family:serif;margin:0}}header{{padding:40px;border-bottom:10px solid #000}}</style></head><body><header><h1 style='font-size:70px;letter-spacing:-5px;margin:0;'>BROKENOMORE</h1><p>{datetime.now().strftime('%B %d, %Y')}</p></header><div style='max-width:1100px;margin:auto;'>{items}</div></body></html>")

if __name__ == "__main__": run() 
