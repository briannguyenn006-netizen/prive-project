import feedparser, os, random, time, requests
from datetime import datetime
from bs4 import BeautifulSoup

# BNM TERMINAL - GROQ ENGINE (LLAMA 3 70B)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def analyze_with_groq(title, summary):
    if not GROQ_API_KEY: return summary
    
    # Lệnh cực gắt cho Llama 3
    prompt = f"""
    ACT AS A SENIOR WALL STREET ANALYST. 
    Write a 500-word JAW-DROPPING financial report for: {title}. 
    Context: {summary}. 
    
    REQUIREMENTS:
    - 4 massive paragraphs.
    - Professional, aggressive English.
    - NO bolding (**), NO bullet points.
    - Focus on Market Impact and Institutional Sentiment.
    - DO NOT BE BRIEF.
    """
    
    payload = {
        "model": "llama3-70b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers, timeout=30)
        res_data = response.json()
        content = res_data['choices'][0]['message']['content']
        return content.replace('**', '').strip()
    except Exception as e:
        print(f"Error calling Groq: {e}")
        return summary

def run():
    posts_dir = 'posts'
    if not os.path.exists(posts_dir): os.makedirs(posts_dir)
    articles = []
    v = int(time.time())
    
    # Lấy tin từ CNBC
    feed = feedparser.parse('https://www.cnbc.com/id/10000667/device/rss/rss.html')
    
    for e in feed.entries[:10]:
        # Fix ảnh: Keyword từ tiêu đề + ID ngẫu nhiên để không bao giờ trùng
        keyword = e.title.split()[0] if e.title else "finance"
        img = f"https://source.unsplash.com/featured/800x500?{keyword},wallstreet&sig={random.randint(1,9999)}"
        
        summary_raw = BeautifulSoup(e.summary, 'html.parser').get_text()
        # Gọi con não Llama 3 của Groq
        full_analysis = analyze_with_groq(e.title, summary_raw)
        
        fname = f"{datetime.now().strftime('%H%M%S')}-{random.randint(10,99)}.html"
        path = os.path.join(posts_dir, fname)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(f"""
            <html><head><meta charset='UTF-8'><title>{e.title}</title>
            <link rel="icon" href="../favicon.png?v={v}">
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;900&display=swap" rel="stylesheet">
            <style>
                body{{font-family:'Inter', sans-serif; max-width:850px; margin:0 auto; padding:60px 20px; line-height:2; color:#111; background:#fff}}
                .back{{font-weight:900; text-decoration:none; color:#000; font-size:14px; text-transform:uppercase}}
                h1{{font-size:50px; font-weight:900; letter-spacing:-3px; line-height:1.1; margin:40px 0}}
                img{{width:100%; border-radius:4px; margin-bottom:40px; box-shadow:0 15px 35px rgba(0,0,0,0.1)}}
                p{{font-size:20px; text-align:justify; white-space:pre-wrap}}
            </style></head>
            <body><a href="../index.html?v={v}" class="back">← TERMINAL</a><h1>{e.title}</h1><img src="{img}"><p>{full_analysis}</p></body></html>
            """)
        articles.append({'t': e.title, 'p': path, 's': full_analysis[:250], 'img': img, 'time': datetime.now().strftime('%H:%M')})

    # Render Index.html
    hero = articles[0]
    side = "".join([f"<div style='margin-bottom:20px; border-bottom:1px solid #eee; padding-bottom:10px;'><span style='color:red; font-size:10px; font-weight:900;'>{a['time']}</span><br><a href='{a['p']}?v={v}' style='color:#000; text-decoration:none; font-weight:700;'>{a['t']}</a></div>" for a in articles[1:10]])
    grid = "".join([f"<div><img src='{a['img']}' style='width:100%; height:220px; object-fit:cover; border-radius:4px;'><h3 style='font-size:20px; font-weight:900; margin:15px 0 10px;'><a href='{a['p']}?v={v}' style='color:#000; text-decoration:none;'>{a['t']}</a></h3><p style='font-size:14px; color:#666;'>{a['s']}...</p></div>" for a in articles[5:]])

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(f"""
        <!DOCTYPE html><html><head><meta charset='UTF-8'><title>BrokeNoMore</title>
        <link rel="icon" href="favicon.png?v={v}">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap" rel="stylesheet">
        <style>
            body{{font-family:'Inter', sans-serif; margin:0; background:#fff}}
            header{{padding:30px 5%; border-bottom:8px solid #000}}
            .logo{{font-size:45px; font-weight:900; text-decoration:none; color:#000; letter-spacing:-3px; text-transform:uppercase}}
            .container{{max-width:1400px; margin:40px auto; padding:0 20px; display:grid; grid-template-columns:2.5fr 1fr; gap:60px}}
            .grid{{display:grid; grid-template-columns:1fr 1fr; gap:30px; margin-top:40px; border-top:5px solid #000; padding-top:30px}}
        </style></head>
        <body><header><a href="/" class="logo">BrokeNoMore</a></header>
        <div class="container">
            <div>
                <img src="{hero['img']}" style="width:100%; height:550px; object-fit:cover;">
                <h1 style="font-size:55px; font-weight:900; letter-spacing:-4px; margin:25px 0; line-height:1;"><a href="{hero['p']}?v={v}" style="color:#000; text-decoration:none;">{hero['t']}</a></h1>
                <p style="font-size:22px; color:#333;">{hero['s']}...</p>
                <div class="grid">{grid}</div>
            </div>
            <div style="border-left:3px solid #000; padding-left:35px;">
                <h3 style="border-bottom:6px solid #000; padding-bottom:10px; margin-bottom:25px; font-weight:900; font-size:14px; text-transform:uppercase;">Latest</h3>
                {side}
            </div>
        </div></body></html>
        """)

if __name__ == "__main__": run()
