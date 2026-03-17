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

RSS_SOURCES = {
    'Reuters Business': 'http://feeds.reuters.com/reuters/businessNews',
    'CNBC Markets': 'https://www.cnbc.com/id/10000667/device/rss/rss.html',
    'WSJ Business': 'https://feeds.a.dj.com/rss/WSJcomUSBusiness.xml'
}

def get_thumbnail(entry):
    if 'media_content' in entry:
        return entry.media_content[0]['url']
    if 'enclosures' in entry and len(entry.enclosures) > 0:
        return entry.enclosures[0]['url']
    summary = entry.summary if 'summary' in entry else ""
    soup = BeautifulSoup(summary, 'html.parser')
    img = soup.find('img')
    return img['src'] if img else "https://images.unsplash.com/photo-1611974717482-58a252c85aec?q=80&w=1000&auto=format&fit=crop"

def rewrite_with_ai(title, summary):
    prompt = f"Summarize this news in 3 professional, punchy sentences for a premium financial terminal. Title: {title}. Content: {summary}"
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except:
        return f"Market Intelligence Report for {title}. Analysis in progress."

def run_auto_news():
    posts_dir = 'posts'
    if not os.path.exists(posts_dir): os.makedirs(posts_dir)
    
    all_articles = []
    print("🚀 Re-engineering Terminal Layout...")

    for provider, url in RSS_SOURCES.items():
        feed = feedparser.parse(url)
        for entry in feed.entries[:4]:
            thumb = get_thumbnail(entry)
            raw_summary = entry.summary if 'summary' in entry else ""
            clean_summary = BeautifulSoup(raw_summary, 'html.parser').get_text()
            ai_content = rewrite_with_ai(entry.title, clean_summary)
            
            clean_title = "".join(x for x in entry.title if x.isalnum() or x==" ")
            filename = f"{datetime.now().strftime('%H%M%S')}-{clean_title[:20]}.html"
            filepath = os.path.join(posts_dir, filename)
            
            # Trang chi tiết bài viết
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"""
                <html><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'>
                <link rel="icon" type="image/png" href="../favicon.png">
                <link href='https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@400;500&display=swap' rel='stylesheet'>
                <style>
                    body {{ font-family: 'Inter', sans-serif; line-height: 1.6; color: #1a1a1a; max-width: 750px; margin: 0 auto; padding: 40px 20px; }}
                    .kicker {{ color: #cc0000; font-weight: 700; text-transform: uppercase; font-size: 12px; letter-spacing: 1px; margin-bottom: 10px; display: block; }}
                    h1 {{ font-family: 'Playfair Display', serif; font-size: 42px; line-height: 1.1; margin-bottom: 20px; }}
                    .meta {{ color: #666; font-size: 14px; border-bottom: 1px solid #eee; padding-bottom: 20px; margin-bottom: 30px; }}
                    img {{ width: 100%; height: auto; border-radius: 2px; margin-bottom: 30px; }}
                    .content {{ font-size: 18px; color: #333; }}
                    .back {{ margin-top: 50px; display: block; text-decoration: none; color: #000; font-weight: 700; font-size: 14px; text-transform: uppercase; border: 1px solid #000; width: fit-content; padding: 10px 20px; }}
                </style></head>
                <body>
                    <span class='kicker'>{provider}</span>
                    <h1>{entry.title}</h1>
                    <div class='meta'>Updated {datetime.now().strftime('%B %d, %Y')} • AI Intelligence Service</div>
                    <img src='{thumb}'>
                    <div class='content'>{ai_content}</div>
                    <a href='../index.html' class='back'>← Return to Terminal</a>
                </body></html>
                """)
            
            all_articles.append({
                'title': entry.title,
                'provider': provider,
                'thumb': thumb,
                'path': filepath,
                'summary': ai_content,
                'time': datetime.now().strftime('%H:%M')
            })

    # Phân loại bài viết: 1 bài chính, còn lại là bài phụ
    hero = all_articles[0]
    side_news = all_articles[1:6]
    grid_news = all_articles[6:]

    side_news_html = "".join([f"""
        <div class='side-item'>
            <span class='time'>{a['time']}</span>
            <a href='{a['path']}'>{a['title']}</a>
        </div>
    """ for a in side_news])

    grid_news_html = "".join([f"""
        <div class='grid-item'>
            <img src='{a['thumb']}'>
            <div class='grid-content'>
                <span class='meta'>{a['provider']}</span>
                <a href='{a['path']}'>{a['title']}</a>
            </div>
        </div>
    """ for a in grid_news])

    # Giao diện TRANG CHỦ (Bloomberg/Reuters Style)
    index_content = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="icon" type="image/png" href="favicon.png">
        <title>BROKENOMORE | Financial Intelligence</title>
        <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
        <style>
            :root {{ --bg: #ffffff; --text: #121212; --accent: #cc0000; --border: #e5e5e5; }}
            body {{ font-family: 'Inter', sans-serif; margin: 0; background: var(--bg); color: var(--text); }}
            
            header {{ border-bottom: 4px solid var(--text); padding: 20px 0; margin: 0 5%; text-align: center; }}
            .logo {{ font-family: 'Playfair Display', serif; font-size: 48px; font-weight: 900; letter-spacing: -2px; }}
            
            .ticker-wrap {{ background: #000; color: #fff; padding: 10px 0; }}
            
            .main-container {{ max-width: 1280px; margin: 30px auto; padding: 0 20px; display: grid; grid-template-columns: 2fr 1fr; gap: 40px; }}
            
            /* Hero Section */
            .hero-article img {{ width: 100%; height: 450px; object-fit: cover; }}
            .hero-article h2 {{ font-family: 'Playfair Display', serif; font-size: 38px; margin: 20px 0 10px; line-height: 1.1; }}
            .hero-article h2 a {{ text-decoration: none; color: inherit; }}
            .hero-article p {{ font-size: 16px; color: #444; line-height: 1.5; }}

            /* Side News */
            .side-news {{ border-left: 1px solid var(--border); padding-left: 40px; }}
            .section-title {{ font-size: 14px; font-weight: 700; text-transform: uppercase; border-bottom: 2px solid var(--text); padding-bottom: 5px; margin-bottom: 20px; display: block; }}
            .side-item {{ margin-bottom: 20px; padding-bottom: 15px; border-bottom: 1px solid var(--border); }}
            .side-item .time {{ font-size: 11px; font-weight: 700; color: var(--accent); display: block; }}
            .side-item a {{ text-decoration: none; color: var(--text); font-weight: 600; font-size: 16px; line-height: 1.3; display: block; margin-top: 5px; }}
            
            /* Market Section */
            .market-sidebar {{ margin-top: 40px; }}
            .market-card {{ background: #f9f9f9; padding: 20px; border-top: 3px solid var(--text); }}

            /* Grid Section */
            .bottom-grid {{ grid-column: 1 / span 2; display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; border-top: 1px solid var(--border); padding-top: 40px; }}
            .grid-item img {{ width: 100%; height: 150px; object-fit: cover; }}
            .grid-item a {{ text-decoration: none; color: var(--text); font-weight: 700; font-size: 15px; display: block; margin-top: 10px; line-height: 1.3; }}
            .grid-item .meta {{ font-size: 11px; text-transform: uppercase; color: #666; font-weight: 600; }}

            @media (max-width: 900px) {{
                .main-container {{ grid-template-columns: 1fr; }}
                .side-news {{ border-left: none; padding-left: 0; }}
                .bottom-grid {{ grid-template-columns: 1fr 1fr; }}
            }}
        </style>
    </head>
    <body>
        <header><div class="logo">BROKENOMORE</div></header>

        <div class="ticker-wrap">
            <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
            {{ "symbols": [
                {{"proName": "OANDA:XAUUSD", "title": "GOLD"}},
                {{"proName": "BITSTAMP:BTCUSD", "title": "BTC"}},
                {{"proName": "FX_IDC:USDVND", "title": "USDVND"}},
                {{"proName": "NASDAQ:NDX", "title": "NASDAQ"}}
            ], "colorTheme": "dark", "isTransparent": false, "displayMode": "adaptive", "locale": "vi_VN" }}
            </script>
        </div>

        <div class="main-container">
            <div class="hero-section">
                <div class="hero-article">
                    <img src="{hero['thumb']}">
                    <h2><a href="{hero['path']}">{hero['title']}</a></h2>
                    <p>{hero['summary']}</p>
                </div>
                
                <div class="market-sidebar">
                    <span class="section-title">Market Analysis</span>
                    <div style="height: 400px;">
                        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
                        <script type="text/javascript">
                        new TradingView.widget({{ "autosize": true, "symbol": "NASDAQ:NDX", "interval": "D", "theme": "light", "style": "3", "locale": "vi_VN", "container_id": "tv_chart" }});
                        </script>
                        <div id="tv_chart" style="height: 100%;"></div>
                    </div>
                </div>
            </div>

            <div class="side-news">
                <span class="section-title">Latest Intelligence</span>
                {side_news_html}
                
                <div class="market-card" style="margin-top: 30px;">
                    <span class="section-title">Quick Look</span>
                    <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-market-overview.js" async>
                    {{ "colorTheme": "light", "dateRange": "12M", "showChart": false, "locale": "vi_VN", "largeChartUrl": "", "isTransparent": false, "width": "100%", "height": "400",
                       "tabs": [ {{ "title": "Indices", "symbols": [ {{ "s": "FOREXCOM:SPX3500" }}, {{ "s": "FOREXCOM:DJI" }}, {{ "s": "INDEX:DXY" }} ] }} ] }}
                    </script>
                </div>
            </div>

            <div class="bottom-grid">
                {grid_news_html}
            </div>
        </div>

        <footer style="border-top: 1px solid #eee; padding: 40px 5%; text-align: center; font-size: 12px; color: #666; background: #f9f9f9;">
            <p>&copy; 2026 BROKENOMORE TERMINAL | DATA POWERED BY REUTERS & CNBC</p>
        </footer>
    </body>
    </html>
    """
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(index_content)
    
    print("✅ MISSION ACCOMPLISHED!")

if __name__ == "__main__":
    run_auto_news()
