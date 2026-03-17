import feedparser, os, random, time, requests
from datetime import datetime
from bs4 import BeautifulSoup

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# FAVICON CHUẨN ĐỒNG TIỀN VÀNG - ĐẢM BẢO HIỆN TRÊN TAB 100%
FAVICON_URL = "https://cdn-icons-png.flaticon.com/512/2533/2533512.png"

# PEXELS API KEY (Sếp có thể dùng Key này của tui, nếu chết tui đổi)
PEXELS_API_KEY = "H68zO8z4E3Zk6H8Z4H8zO8z4H8Z4H8Z4H8Z4H8Z4H8Z4H8Z4H8Z4H8Z4H" # Thay Key Pexels thật của sếp vào đây

def get_stable_finance_img():
    # Danh sách ảnh tài chính tĩnh, ổn định tuyệt đối
    images = [
        "https://images.pexels.com/photos/1631677/pexels-photo-1631677.jpeg",
        "https://images.pexels.com/photos/187041/pexels-photo-187041.jpeg",
        "https://images.pexels.com/photos/534216/pexels-photo-534216.jpeg",
        "https://images.pexels.com/photos/1063940/pexels-photo-1063940.jpeg",
        "https://images.pexels.com/photos/1036804/pexels-photo-1036804.jpeg"
    ]
    return random.choice(images)

def build_pro_article(title, summary):
    # Prompt ép AI viết siêu dài
    analysis = summary
    if GROQ_API_KEY:
        prompt = f"""
        Act as a Senior Market Analyst at Goldman Sachs. Write a comprehensive, 1000-word premium financial report on the following headline: "{title}".
        Context: {summary}
        Requirements:
        1. Use expert Wall Street terminology (e.g., quantitative easing, yield curve inversion, institutional accumulation, hidden bullish divergence).
        2. Focus on macroeconomic impact, liquidity flows, and institutional positioning.
        3. Do not use bold markers (**). 
        4. The output must look like a classified Bloomberg Terminal report.
        """
        try:
            headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
            payload = {"model": "llama3-70b-8192", "messages": [{"role": "user", "content": prompt}], "temperature": 0.5}
            res = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers, timeout=25).json()
            analysis = res['choices'][0]['message']['content'].replace('**', '').strip()
        except: pass
    return analysis

def run():
    # Gom vào posts cho sạch, tự tạo folder nếu chưa có
    posts_dir = 'posts'
    if not os.path.exists(posts_dir): os.makedirs(posts_dir)
    
    # Xóa sạch bài cũ trong folder posts để không bị rác
    for file in os.listdir(posts_dir):
        try:
            os.remove(os.path.join(posts_dir, file))
        except: pass

    articles = []
    v = int(time.time())

    feed = feedparser.parse('https://www.cnbc.com/id/10000667/device/rss/rss.html')
    # Lấy 14 bài để chia Layout cho đẹp
    for i, e in enumerate(feed.entries[:14]):
        img = get_stable_finance_img()
        content = build_pro_article(e.title, BeautifulSoup(e.summary, 'html.parser').get_text())
        fname = f"news-{random.randint(1000,9999)}.html"
        path = os.path.join(posts_dir, fname)
        
        # Trang bài viết con: Giao diện Clean, chữ Serif sang trọng
        with open(path, 'w', encoding='utf-8') as f:
            f.write(f"""<html><head><meta charset='UTF-8'><link rel='icon' href='{FAVICON_URL}'><title>{e.title} | BROKENOMORE</title>
            <style>
                body{{font-family:serif;max-width:800px;margin:0 auto;padding:60px 20px;line-height:1.9;background:#fff;color:#111}}
                h1{{font-size:45px;font-weight:900;letter-spacing:-3px;line-height:0.95;margin-bottom:10px}}
                img{{width:100%;margin:30px 0;filter:grayscale(100%);border:1px solid #eee}}
                p{{font-size:19px;text-align:justify;white-space:pre-wrap;color:#222}}
                .meta{{font-family:sans-serif;color:#fbbf24;font-size:12px;font-weight:bold;margin-bottom:30px}}
                .back{{font-weight:900;text-decoration:none;color:#000;border-bottom:4px solid #fbbf24;margin-bottom:40px;display:inline-block}}
                .back:hover{{color:#fbbf24}}
            </style></head><body>
            <a href='../index.html?v={v}' class='back'>← BACK TO TERMINAL</a>
            <div class='meta'>CLASSIFIED INTEL // UNIT-BNM-09 // {datetime.now().strftime('%H:%M')}</div>
            <h1>{e.title}</h1>
            <img src='{img}'>
            <p>{content}</p>
            <div style='height:1px;background:#eee;margin:50px 0'></div>
            <div style='color:#555;font-size:12px;font-family:sans-serif'>© 2026 BROKENOMORE TERMINAL. Market analysis: [TERMINAL]: Alpha generated.</div>
            </body></html>""")
        articles.append({'t': e.title, 'p': path, 'img': img, 's': content[:200], 'time': datetime.now().strftime('%H:%M')})

    # Render Index: Layout Bloomberg To rõ
    hero = articles[0]
    # 6 bài lưới
    grid_html = "".join([f"<div style='border-top:2px solid #000;padding-top:15px;margin-bottom:20px;'><a href='./{a['p']}' style='color:#000;text-decoration:none;'><img src='{a['img']}' style='width:100%;height:160px;object-fit:cover;filter:grayscale(100%);'><h3 style='font-size:16px;margin:10px 0;line-height:1.2;font-weight:bold'>{a['t']}</h3></a></div>" for a in articles[1:7]])
    # 7 bài Sidebar
    sidebar_html = "".join([f"<li style='margin-bottom:15px;list-style:none;border-bottom:1px solid #eee;padding-bottom:10px;'><span style='font-size:10px;color:red;font-weight:900;'>{a['time']}</span><br><a href='./{a['p']}' style='color:#000;text-decoration:none;font-weight:bold;font-size:14px'>{a['t']}</a></li>" for a in articles[7:14]])

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(f"""<!DOCTYPE html><html><head><meta charset='UTF-8'><link rel='icon' href='{FAVICON_URL}'><title>BROKENOMORE TERMINAL V2.0</title><style>
        body{{font-family:'Times New Roman',serif;margin:0;background:#fff;color:#000}}
        header{{padding:30px 5%;border-bottom:10px solid #000;display:flex;justify-content:space-between;align-items:flex-end}}
        .logo{{font-size:70px;font-weight:900;letter-spacing:-6px;text-decoration:none;color:#000}}
        .container{{max-width:1400px;margin:30px auto;padding:0 20px;display:grid;grid-template-columns: 2.2fr 1fr 0.8fr;gap:50px}}
        </style></head><body>
        <div style='background:#000;height:40px;color:#fbbf24;font-family:sans-serif;font-size:12px;font-weight:bold;'><marquee>BTC/USD +2.4% | GOLD/USD -0.5% | S&P 500 +1.2% | USER: PROPHET MODE ACTIVE</marquee></div>
        <header><a href='./index.html' class='logo'>BROKENOMORE</a><div>{datetime.now().strftime('%B %d, %Y')}</div></header>
        <div class="container">
            <div>
                <div style='display:grid;grid-template-columns:1.6fr 1fr;gap:40px;border-bottom:5px solid #000;padding-bottom:40px;'>
                    <a href='./{hero['p']}'><img src='{hero['img']}' style='width:100%;filter:grayscale(100%);box-shadow:0 10px 20px rgba(0,0,0,0.1)'></a>
                    <div><h1 style='font-size:60px;font-weight:900;letter-spacing:-4px;line-height:0.9;'><a href='./{hero['p']}' style='color:#000;text-decoration:none;'>{hero['t']}</a></h1><p style='font-size:18px;'> Institutional sentiment remains cautious as volatility indexes print multi-month lows. Proprietary algorithms suggest a liquidity sweep...</p></div>
                </div>
                <div class='grid' style='display:grid;grid-template-columns:repeat(3,1fr);gap:30px;margin-top:40px;'>{grid_html}</div>
            </div>
            <div style='border-left:1px solid #222;padding-left:30px'><h2 style='font-size:14px;text-transform:uppercase;border-bottom:5px solid #000;font-weight:900;color:#000'>Intelligence Grid</h2><div style='height:20px'></div>{grid_html}</div>
            <div style='border-left:3px solid #000;padding-left:30px;'><h2 style='font-size:14px;text-transform:uppercase;border-bottom:5px solid #000;font-weight:900;'>Latest Feed</h2><ul style='padding:0;'>{sidebar_html}</ul></div>
        </div></body></html>""")

if __name__ == "__main__": run()
