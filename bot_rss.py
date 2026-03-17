import feedparser
import os
import re
import random
import time
from datetime import datetime
from bs4 import BeautifulSoup
import google.generativeai as genai

# ==========================================
# CẤU HÌNH AI
# ==========================================
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

RSS_SOURCES = {
    'Global Desk': 'http://feeds.reuters.com/reuters/businessNews',
    'Market Intelligence': 'https://www.cnbc.com/id/10000667/device/rss/rss.html',
    'Institutional Report': 'https://feeds.a.dj.com/rss/WSJcomUSBusiness.xml'
}

def get_thumbnail(entry):
    img_url = ""
    if 'media_content' in entry: img_url = entry.media_content[0]['url']
    elif 'enclosures' in entry and len(entry.enclosures) > 0: img_url = entry.enclosures[0]['url']
    
    stock_images = [
        "https://images.unsplash.com/photo-1611974717482-58a252c85aec?auto=format&fit=crop&w=1200",
        "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?auto=format&fit=crop&w=1200",
        "https://images.unsplash.com/photo-1640343830005-ee0505d307bb?auto=format&fit=crop&w=1200",
        "https://images.unsplash.com/photo-1633156191771-700947264a2c?auto=format&fit=crop&w=1200"
    ]
    # Nếu link ảnh chứa mấy cái tracker rác hoặc trống thì đổi sang ảnh xịn ngay
    if not img_url or any(x in img_url for x in ["doubleclick", "feeds.feedburner", "pixel"]):
        return random.choice(stock_images)
    return img_url

def rewrite_with_ai(title, summary):
    # Prompt "gắt" hơn, ép viết dài ít nhất 350 từ
    prompt = f"""
    Act as the Chief Market Strategist at BrokeNoMore. 
    Rewrite this news into a detailed institutional market report (minimum 350 words).
    
    Structure your analysis into 3 clear sections:
    1. INSTITUTIONAL CONTEXT: Deep dive into the macro environment.
    2. QUANTITATIVE ANALYSIS: Potential impact on liquidity and market volatility.
    3. STRATEGIC POSITIONING: How a professional fund manager should view this.
    
    Style: Cold, professional, data-driven. Do NOT use bold (**). Do NOT mention news agencies. 
    Write at least 4-5 long sentences per section.
    
    Title: {title}
    Data: {summary}
    """
    try:
        response = model.generate_content(prompt)
        text = response.text.strip().replace('**', '')
        # Nếu AI trả về quá ngắn (dưới 500 ký tự), coi như lỗi để dùng fallback
        if len(text) < 500: raise Exception("Too short")
        return text
    except:
        # Fallback bài viết mẫu chuyên nghiệp nếu AI dở chứng
        return f"The tactical assessment for {title} is currently being processed by our global research team. Initial indicators suggest a significant shift in market sentiment. Our quantitative models are currently evaluating the long-term impact on global liquidity and sector-specific volatility. We expect to provide a full-scale institutional breakdown within the hour. Investors are advised to maintain current hedged positions until the BNM Intelligence Desk confirms the final risk-reward ratio for this event."

def run_auto_news():
    posts_dir = 'posts'
    if not os.path.exists(posts_dir): os.makedirs(posts_dir)
    all_articles = []
    v_id = int(time.time())

    for provider, url in RSS_SOURCES.items():
        feed = feedparser.parse(url)
        for entry in feed.entries[:3]:
            thumb = get_thumbnail(entry)
            clean_summary = BeautifulSoup(entry.summary, 'html.parser').get_text() if 'summary' in entry else "Data pending."
            ai_content = rewrite_with_ai(entry.title, clean_summary)
            
            clean_title = "".join(x for x in entry.title if x.isalnum() or x==" ")
            filename = f"{datetime.now().strftime('%H%M%S')}-{clean_title[:20]}.html"
            filepath = os.path.join(posts_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"""
                <html><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'>
                <title>{entry.title} | BrokeNoMore</title>
                <link rel="icon" type="image/png" href="../favicon.png?v={v_id}">
                <link href='https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap' rel='stylesheet'>
                <style>
                    body {{ font-family: 'Inter', sans-serif; line-height: 1.8; color: #111; max-width: 850px; margin: 0 auto; padding: 60px 20px; background: #fff; }}
                    header {{ margin-bottom: 50px; border-bottom: 2px solid #000; padding-bottom: 20px; }}
                    .logo {{ font-weight: 900; font-size: 24px; text-transform: uppercase; text-decoration: none; color: #000; }}
                    h1 {{ font-size: 44px; font-weight: 900; line-height: 1.1; margin: 30px 0; letter-spacing: -2px; color: #000; }}
                    img {{ width: 100%; border-radius: 4px; margin-bottom: 40px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); }}
                    .content {{ font-size: 20px; color: #222; white-space: pre-wrap; }}
                    .back {{ margin-top: 60px; display: inline-block; font-weight: 900; color: #000; text-decoration: none; border-bottom: 3px solid #000; padding-bottom: 5px; text-transform: uppercase; }}
                </style></head>
                <body>
                    <header><a href="../index.html?v={v_id}" class="logo">BrokeNoMore</a></header>
                    <h1>{entry.title}</h1>
                    <div style='color:#666; font-size:13px; margin-bottom:40px; text-transform:uppercase;'>{datetime.now().strftime('%B %d, %Y')} • Filed by BrokeNoMore Research</div>
                    <img src='{thumb}'>
                    <div class='content'>{ai_content}</div>
                    <a href='../index.html?v={v_id}' class='back'>← Return to Market Terminal</a>
                </body></html>
                """)
            all_articles.append({'title': entry.title, 'provider': provider, 'thumb': thumb, 'path': filepath, 'summary': ai_content[:250]+"...", 'time': datetime.now().strftime('%H:%M')})

    # Render Index.html
    hero = all_articles[0]
    side_html = "".join([f"<div style='margin-bottom:25px; border-bottom:1px solid #eee; padding-bottom:15px;'><span style='font-size:11px; color:#cc0000; font-weight:900;'>{a['time']}</span><br><a href='{a['path']}?v={v_id}' style='text-decoration:none; color:#000; font-weight:700; font-size:18px; line-height:1.2; display:block; margin-top:5px;'>{a['title']}</a></div>" for a in all_articles[1:6]])
    grid_html = "".join([f"<div style='margin-bottom:40px;'><img src='{a['thumb']}' style='width:100%; height:180px; object-fit:cover; border-radius:3px;'><a href='{a['path']}?v={v_id}' style='text-decoration:none; color:#000; font-weight:700; font-size:18px; display:block; margin-top:15px; line-height:1.3;'>{a['title']}</a></div>" for a in all_articles[6:]])

    index_content = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <title>BrokeNoMore | Terminal</title>
        <link rel="icon" type="image/png" href="favicon.png?v={v_id}">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Inter', sans-serif; margin: 0; background: #fff; color: #000; }}
            header {{ padding: 30px 5%; border-bottom: 4px solid #000; }}
            .logo {{ font-size: 36px; font-weight: 900; text-transform: uppercase; text-decoration: none; color: #000; letter-spacing: -2px; }}
            .main-container {{ max-width: 1400px; margin: 40px auto; padding: 0 30px; display: grid; grid-template-columns: 2.3fr 1fr; gap: 60px; }}
            .hero-img {{ width: 100%; height: 550px; object-fit: cover; border-radius: 4px; }}
            .hero-title {{ font-size: 52px; font-weight: 900; line-height: 1; margin: 30px 0 20px; letter-spacing: -3px; }}
            @media (max-width: 1000px) {{ .main-container {{ grid-template-columns: 1fr; }} }}
        </style>
    </head>
    <body>
        <header><a href="/" class="logo">BrokeNoMore</a></header>
        <div class="main-container">
            <div>
                <img src="{hero['thumb']}" class="hero-img">
                <h2 class="hero-title"><a href="{hero['path']}?v={v_id}" style="text-decoration:none; color:#000;">{hero['title']}</a></h2>
                <p style="font-size:20px; color:#333; line-height:1.7;">{hero['summary']}</p>
                <div style="margin-top:50px; display:grid; grid-template-columns: 1fr 1fr; gap:40px; border-top:4px solid #000; padding-top:40px;">{grid_html}</div>
            </div>
            <div style="border-left: 1px solid #eee; padding-left: 40px;">
                <h3 style="font-size:14px; text-transform:uppercase; border-bottom:3px solid #000; padding-bottom:8px; margin-bottom:30px; font-weight:900;">Latest</h3>
                {side_html}
            </div>
        </div>
    </body>
    </html>
    """
    with open('index.html', 'w', encoding='utf-8') as f: f.write(index_content)

if __name__ == "__main__":
    run_auto_news()
