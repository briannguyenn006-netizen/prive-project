import feedparser
import os  # Dòng này cực kỳ quan trọng để chạy tự động
import re
from datetime import datetime
from bs4 import BeautifulSoup
import google.generativeai as genai

# ==========================================
# 1. CẤU HÌNH AI (LẤY TỪ HỆ THỐNG BẢO MẬT)
# ==========================================
# Khi chạy trên GitHub, nó sẽ tự lấy Key sếp đã dán trong phần Settings Secrets
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    print("⚠️ Lỗi: Không tìm thấy API Key. Sếp nhớ thiết lập Secret trên GitHub nhé!")
else:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

# Nguồn tin quốc tế
RSS_SOURCES = {
    'Reuters': 'http://feeds.reuters.com/reuters/businessNews',
    'CNBC': 'https://www.cnbc.com/id/10000667/device/rss/rss.html',
    'BBC World': 'http://feeds.bbci.co.uk/news/world/rss.xml'
}

def get_thumbnail(entry):
    """Tìm ảnh thumbnail từ dữ liệu RSS"""
    if 'media_content' in entry:
        return entry.media_content[0]['url']
    if 'enclosures' in entry and len(entry.enclosures) > 0:
        return entry.enclosures[0]['url']
    summary = entry.summary if 'summary' in entry else ""
    soup = BeautifulSoup(summary, 'html.parser')
    img = soup.find('img')
    return img['src'] if img else "https://via.placeholder.com/600x400.png?text=BrokeNoMore+News"

def rewrite_with_ai(title, summary):
    """AI xào nấu lại tin tức bằng tiếng Anh chuyên nghiệp"""
    prompt = f"""
    Rewrite the following news article in professional, engaging English.
    Objective: Create a concise summary (3-4 sentences) that avoids plagiarism.
    Tone: Global Financial News.
    
    Original Title: {title}
    Original Content: {summary}
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Summary: {title} (AI rewrite temporarily unavailable)."

def run_auto_news():
    posts_dir = 'posts'
    if not os.path.exists(posts_dir): os.makedirs(posts_dir)
    
    news_items_html = []
    print("🚀 Global AI Bot is starting...")

    for provider, url in RSS_SOURCES.items():
        print(f"📡 Fetching from: {provider}")
        feed = feedparser.parse(url)
        
        for entry in feed.entries[:3]:
            thumb = get_thumbnail(entry)
            raw_summary = entry.summary if 'summary' in entry else ""
            clean_summary = BeautifulSoup(raw_summary, 'html.parser').get_text()
            
            print(f"🤖 AI is rewriting: {entry.title[:50]}...")
            ai_content = rewrite_with_ai(entry.title, clean_summary)
            
            clean_title = "".join(x for x in entry.title if x.isalnum() or x==" ")
            filename = f"{datetime.now().strftime('%H%M%S')}-{clean_title[:20]}.html"
            filepath = os.path.join(posts_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"""
                <html>
                <head><meta charset='UTF-8'></head>
                <body style='font-family:sans-serif;background:#f8fafc;padding:40px;line-height:1.7;max-width:800px;margin:auto;'>
                    <div style='background:white;padding:30px;border-radius:20px;box-shadow:0 10px 25px rgba(0,0,0,0.05);'>
                        <img src='{thumb}' style='width:100%;border-radius:15px;margin-bottom:20px;'>
                        <h1 style='color:#1e293b;'>{entry.title}</h1>
                        <p style='color:#64748b;'>Source: {provider} | {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
                        <hr style='border:0;border-top:1px solid #eee;margin:20px 0;'>
                        <div style='font-size:1.2rem;color:#334155;'>{ai_content}</div>
                        <br><a href='../index.html' style='color:#3b82f6;text-decoration:none;font-weight:bold;'>← Back to Home</a>
                    </div>
                </body></html>
                """)
            
            news_items_html.append(f"""
                <div style='margin-bottom:20px;padding:20px;background:#1e293b;border-radius:15px;display:flex;gap:20px;align-items:center;'>
                    <img src='{thumb}' style='width:150px;height:100px;object-fit:cover;border-radius:10px;'>
                    <div>
                        <a href='{filepath}' style='color:#38bdf8;text-decoration:none;font-weight:bold;font-size:1.2rem;'>{entry.title}</a>
                        <p style='color:#94a3b8;font-size:0.85rem;margin-top:8px;'>{provider} • {datetime.now().strftime('%b %d, %Y')}</p>
                    </div>
                </div>
            """)

    index_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Global AI News Terminal</title>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; max-width: 900px; margin: 50px auto; background: #0f172a; color: white; padding: 0 20px; }}
            h1 {{ text-align: center; color: #38bdf8; letter-spacing: 2px; font-size: 2.5rem; text-transform: uppercase; }}
        </style>
    </head>
    <body>
        <h1>🌐 GLOBAL NEWS TERMINAL</h1>
        <div style="margin-top:30px;">
            {''.join(news_items_html)}
        </div>
    </body>
    </html>
    """
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(index_content)
    
    print("✅ MISSION ACCOMPLISHED!")

if __name__ == "__main__":
    run_auto_news()