import feedparser
import os
import re
from datetime import datetime
from bs4 import BeautifulSoup
import google.generativeai as genai

# ==========================================
# 1. CẤU HÌNH AI (LẤY TỪ GITHUB SECRETS)
# ==========================================
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    print("⚠️ Lỗi: Không tìm thấy API Key trong Secrets!")
else:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

# Nguồn tin tài chính quốc tế chuẩn Bloomberg/CNBC
RSS_SOURCES = {
    'Reuters Business': 'http://feeds.reuters.com/reuters/businessNews',
    'CNBC Markets': 'https://www.cnbc.com/id/10000667/device/rss/rss.html',
    'Wall Street Journal': 'https://feeds.a.dj.com/rss/WSJcomUSBusiness.xml'
}

def get_thumbnail(entry):
    if 'media_content' in entry:
        return entry.media_content[0]['url']
    if 'enclosures' in entry and len(entry.enclosures) > 0:
        return entry.enclosures[0]['url']
    summary = entry.summary if 'summary' in entry else ""
    soup = BeautifulSoup(summary, 'html.parser')
    img = soup.find('img')
    return img['src'] if img else "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?q=80&w=1000&auto=format&fit=crop"

def rewrite_with_ai(title, summary):
    prompt = f"""
    Rewrite this financial news article for a premium terminal like Bloomberg. 
    Use professional, high-level English. 3-4 concise sentences.
    Title: {title}
    Content: {summary}
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except:
        return f"Market Analysis: {title}. Full report pending internal review."

def run_auto_news():
    posts_dir = 'posts'
    if not os.path.exists(posts_dir): os.makedirs(posts_dir)
    
    news_items_html = []
    print("🚀 Financial AI Bot is initializing...")

    for provider, url in RSS_SOURCES.items():
        print(f"📡 Scanning: {provider}")
        feed = feedparser.parse(url)
        
        for entry in feed.entries[:3]:
            thumb = get_thumbnail(entry)
            raw_summary = entry.summary if 'summary' in entry else ""
            clean_summary = BeautifulSoup(raw_summary, 'html.parser').get_text()
            
            ai_content = rewrite_with_ai(entry.title, clean_summary)
            
            clean_title = "".join(x for x in entry.title if x.isalnum() or x==" ")
            filename = f"{datetime.now().strftime('%H%M%S')}-{clean_title[:20]}.html"
            filepath = os.path.join(posts_dir, filename)
            
            # Giao diện trang con (Chi tiết bài báo)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"""
                <html>
                <head>
                    <meta charset='UTF-8'>
                    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
                    <link href='https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@400&display=swap' rel='stylesheet'>
                    <style>
                        body {{ font-family: 'Inter', sans-serif; background:#fff; padding:20px; color:#121212; line-height:1.8; max-width:800px; margin:auto; }}
                        .header {{ border-bottom: 2px solid #000; padding-bottom: 10px; margin-bottom: 30px; text-transform: uppercase; font-weight: bold; font-size: 14px; color: #004685; }}
                        h1 {{ font-family: 'Playfair Display', serif; font-size: 36px; margin-bottom: 10px; line-height: 1.1; }}
                        img {{ width:100%; border-radius:4px; margin: 20px 0; }}
                        .content {{ font-size: 19px; color: #333; }}
                        .back-btn {{ display:inline-block; margin-top:40px; color:#004685; text-decoration:none; font-weight:bold; border: 1px solid #004685; padding: 10px 20px; border-radius: 4px; }}
                    </style>
                </head>
                <body>
                    <div class='header'>BROKENOMORE | Global Market Intelligence</div>
                    <h1>{entry.title}</h1>
                    <p style='color:#666;'>By AI Intelligence Terminal • {datetime.now().strftime('%b %d, %Y')}</p>
                    <img src='{thumb}'>
                    <div class='content'>{ai_content}</div>
                    <a href='../index.html' class='back-btn'>← Back to Terminal</a>
                </body></html>
                """)
            
            # Khung tin tức ở trang chủ
            news_items_html.append(f"""
                <div class='news-card'>
                    <img src='{thumb}'>
                    <div>
                        <div class='news-meta'>{provider} • {datetime.now().strftime('%H:%M')}</div>
                        <a href='{filepath}'>{entry.title}</a>
                        <p style='color:#555; font-size:15px; margin-top:10px;'>{ai_content[:150]}...</p>
                    </div>
                </div>
            """)

    # Giao diện TRANG CHỦ (Bloomberg Style)
    index_content = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>BROKENOMORE | Professional Market Terminal</title>
        <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@400;700&display=swap" rel="stylesheet">
        <style>
            :root {{ --primary-black: #121212; --accent-blue: #004685; --border-color: #e0e0e0; }}
            body {{ font-family: 'Inter', sans-serif; margin: 0; background: #fff; color: var(--primary-black); }}
            header {{ padding: 20px 5%; border-bottom: 4px solid var(--primary-black); text-align: center; }}
            .logo {{ font-family: 'Playfair Display', serif; font-size: 42px; text-transform: uppercase; margin: 0; letter-spacing: -1px; }}
            .market-widgets {{ border-bottom: 1px solid var(--border-color); background: #fcfcfc; }}
            .chart-container {{ width: 100%; height: 400px; border-bottom: 1px solid var(--border-color); }}
            .container {{ max-width: 1100px; margin: 30px auto; padding: 0 20px; }}
            .date-line {{ text-align: center; font-weight: bold; border-bottom: 1px solid var(--border-color); margin-bottom: 25px; padding-bottom: 10px; text-transform: uppercase; font-size: 12px; color: #666; }}
            .news-card {{ margin-bottom: 20px; padding: 25px 0; border-bottom: 1px solid var(--border-color); display: flex; gap: 25px; align-items: center; }}
            .news-card img {{ width: 220px; height: 140px; object-fit: cover; border-radius: 2px; }}
            .news-card a {{ color: var(--primary-black); text-decoration: none; font-weight: bold; font-size: 1.6rem; font-family: 'Playfair Display', serif; line-height: 1.2; }}
            .news-card a:hover {{ color: var(--accent-blue); }}
            .news-meta {{ color: var(--accent-blue); font-size: 11px; font-weight: bold; text-transform: uppercase; margin-bottom: 8px; }}
            footer {{ background: #121212; color: #fff; padding: 40px 0; text-align: center; margin-top: 60px; font-size: 14px; }}
        </style>
    </head>
    <body>
        <header>
            <div class="logo">BROKENOMORE</div>
            <p style="margin:5px 0 0; font-size:12px; color:#666; letter-spacing: 2px; font-weight:700;">GLOBAL MARKET INTELLIGENCE TERMINAL</p>
        </header>

        <div class="market-widgets">
            <div class="tradingview-widget-container">
                <div class="tradingview-widget-container__widget"></div>
                <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
                {{
                    "symbols": [
                        {{"proName": "FOREXCOM:SPX3500", "title": "S&P 500"}},
                        {{"proName": "FOREXCOM:DJI", "title": "Dow Jones"}},
                        {{"proName": "NASDAQ:NDX", "title": "Nasdaq 100"}},
                        {{"proName": "OANDA:XAUUSD", "title": "Gold"}},
                        {{"proName": "BITSTAMP:BTCUSD", "title": "Bitcoin"}},
                        {{"proName": "FX_IDC:USDVND", "title": "USD/VND"}}
                    ],
                    "showSymbolLogo": true, "colorTheme": "light", "isTransparent": false, "displayMode": "adaptive", "locale": "vi_VN"
                }}
                </script>
            </div>
            <div class="chart-container">
                <div id="tradingview_chart" style="height:100%;width:100%"></div>
                <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
                <script type="text/javascript">
                new TradingView.widget({{
                    "autosize": true, "symbol": "NASDAQ:NDX", "interval": "D", "theme": "light", "style": "1", "locale": "vi_VN", "container_id": "tradingview_chart"
                }});
                </script>
            </div>
        </div>

        <div class="container">
            <div class="date-line">Intelligence Report: {datetime.now().strftime('%d/%m/%Y %H:%M')}</div>
            {''.join(news_items_html)}
        </div>

        <footer>
            <p>&copy; 2026 BROKENOMORE TERMINAL | <a href="privacy.html" style="color:#aaa;">Privacy Policy</a></p>
        </footer>
    </body>
    </html>
    """
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(index_content)
    
    print("✅ MISSION ACCOMPLISHED!")

if __name__ == "__main__":
    run_auto_news()
