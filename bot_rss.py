import feedparser, os, random, time, requests, base64
from datetime import datetime

# Cấu hình hệ thống
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
FAVICON_DATA = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAMAAACdt4HsAAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAAAXVBMVEUAAAAAAAAAAAAAAAD///////////////////////////////////////////////////////////////////////////////////////////////////////////8AAAD///8f8PshAAAAHnRSTlMAAAAAAAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBmHOnYhAAAAAWJLR0QAiAUdSAAAAAlwSFlzAAALEwAACxMBAJqcGAAAAAd0SU1FBmYDEgIcAnv6W3cAAAC+SURBVFjD7dbXDsIwDATQpI0T0vTee//+VzEUCG2SNo7mSOfI8mInK60D0Of0A28mGACvAbD1FzD1X8Xm8Kvh9fD6+Gr4YfhpeD78OjwLfw0vhh+GF8N74fXw6XAcfhh+Gp4Pvw7Pgh9G6wB87vL7fL8/5fDpcB6ehR9G6wB8/un3fH6fy+fD+XAVvhh+Gp4Pvw7Pgh9G6wCs78MNo3UAVvfhjtE6AKv7cNNoHYDVfbht9AdY3Yc7RusArO7DXaM/wHwN0Bf0D2Y6F6O3p83UAAAAJXRFWHRkYXRlOmNyZWF0ZQAyMDI2LTAzLTE4VDAyOjI4OjI4KzA3OjAw0zS0fQAAACV0RVh0ZGF0ZTptb2RpZnkAMjAyNi0wMy0xOFQwMjoyODoyOCswNzowMHLD1qQAAAAASUVORK5CYII="

class BrokenNoMoreTerminal:
    def __init__(self):
        self.posts_dir = 'posts'
        self.v = int(time.time())
        self.img_ids = [
            "1611974714658-058e132215bd", "1590283602057-0165b7bb144c", 
            "1526303306626-d8617ee25f03", "1454165833039-5b30046bb4b7", 
            "1551288049-bb1483384206", "1535320903745-f4675ce80fe7", 
            "1518186414719-2ea2a2080f55", "1642390193051-9876e06385f3"
        ]
        if not os.path.exists(self.posts_dir): os.makedirs(self.posts_dir)

    def generate_analysis(self, title, summary):
        """Hàm phân tích chuyên sâu - Ép AI viết dài"""
        if not GROQ_API_KEY: return summary
        
        prompt = f"""
        ACT AS: Senior Quantitative Analyst at Goldman Sachs.
        TASK: Write a 1000-word deep-dive intelligence report on: "{title}".
        CONTEXT: {summary}
        STRUCTURE:
        1. EXECUTIVE SUMMARY (High-level take)
        2. MARKET IMPACT & LIQUIDITY ANALYSIS (Technical details)
        3. INSTITUTIONAL ORDER FLOW (Smart money positioning)
        4. MACROECONOMIC CORRELATION (Global impact)
        5. STRATEGIC OUTLOOK (Forward-looking guidance)
        STYLE: Aggressive, professional, data-driven. Use complex financial terminology. No bolding.
        """
        try:
            res = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                json={"model": "llama3-70b-8192", "messages": [{"role": "user", "content": prompt}], "temperature": 0.5},
                timeout=30
            ).json()
            return res['choices'][0]['message']['content'].strip()
        except: return summary

    def create_article_page(self, title, content, img_url):
        """Tạo trang chi tiết bài viết với layout sang trọng"""
        fname = f"news-{random.randint(10000, 99999)}.html"
        path = os.path.join(self.posts_dir, fname)
        html = f"""
        <html><head><meta charset='UTF-8'><link rel='icon' href='{FAVICON_DATA}'><title>{title} | BNM</title>
        <style>
            body{{background:#050505;color:#ccc;font-family:'Georgia',serif;margin:0;padding:80px 20px;line-height:1.9;letter-spacing:0.02em}}
            .content{{max-width:850px;margin:auto}}
            .header-nav{{display:flex;align-items:center;gap:10px;color:#fbbf24;text-decoration:none;font-family:sans-serif;font-weight:900;font-size:13px;text-transform:uppercase}}
            h1{{font-size:55px;color:#fff;line-height:1;margin:40px 0;letter-spacing:-2px;font-weight:900;font-family:sans-serif}}
            img{{width:100%;border-radius:2px;border:1px solid #333;margin:40px 0;box-shadow:0 20px 40px rgba(0,0,0,0.5)}}
            p{{font-size:20px;text-align:justify;white-space:pre-wrap;color:#bbb;margin-bottom:30px}}
            .divider{{height:1px;background:#222;margin:50px 0}}
        </style></head><body><div class='content'>
            <a href='../index.html?v={self.v}' class='header-nav'><img src='{FAVICON_DATA}' width='25'> BROKENOMORE TERMINAL</a>
            <h1>{title}</h1>
            <div style='color:#fbbf24;font-family:sans-serif;font-weight:bold'>CLASSIFIED INTEL // UNIT-BNM-09</div>
            <img src='{img_url}'>
            <p>{content}</p>
            <div class='divider'></div>
            <div style='color:#555;font-family:sans-serif;font-size:12px'>SOURCE: BLOOMBERG/REUTERS/CNBC SYNDICATED DATA</div>
        </div></body></html>
        """
        with open(path, 'w', encoding='utf-8') as f: f.write(html)
        return path

    def run(self):
        # Dọn rác
        for f in os.listdir(self.posts_dir): os.remove(os.path.join(self.posts_dir, f))
        
        feed = feedparser.parse('https://www.cnbc.com/id/10000667/device/rss/rss.html')
        articles = []
        
        for i, e in enumerate(feed.entries[:10]):
            img = f"https://images.unsplash.com/photo-{self.img_ids[i % len(self.img_ids)]}?w=1200&q=90&fit=crop"
            content = self.generate_analysis(e.title, e.summary)
            path = self.create_article_page(e.title, content, img)
            articles.append({'t': e.title, 'p': path, 'img': img, 'time': datetime.now().strftime('%H:%M')})

        # Render Trang Chủ
        hero = articles[0]
        grid_html = "".join([f"<div style='border-bottom:1px solid #222;padding-bottom:20px;margin-bottom:20px'><a href='./{a['p']}' style='color:#fff;text-decoration:none'><img src='{a['img']}' style='width:100%;height:180px;object-fit:cover;filter:grayscale(60%)'><h3 style='font-size:18px;margin-top:15px;line-height:1.2'>{a['t']}</h3></a></div>" for a in articles[1:5]])
        feed_html = "".join([f"<li style='list-style:none;margin-bottom:20px;border-bottom:1px solid #111;padding-bottom:10px'><span style='color:#fbbf24;font-size:11px;font-weight:bold'>{a['time']}</span><br><a href='./{a['p']}' style='color:#999;text-decoration:none;font-size:14px;font-weight:bold'>{a['t']}</a></li>" for a in articles[5:]])

        index_html = f"""
        <!DOCTYPE html><html><head><meta charset='UTF-8'><link rel='icon' href='{FAVICON_DATA}'><title>BROKENOMORE TERMINAL</title>
        <style>
            body{{background:#000;color:#fff;font-family:'Helvetica',sans-serif;margin:0}}
            header{{padding:30px 5%;border-bottom:8px solid #fff;display:flex;justify-content:space-between;align-items:center}}
            .logo{{display:flex;align-items:center;gap:20px;text-decoration:none;color:#fff;font-size:65px;font-weight:900;letter-spacing:-5px;font-family:serif}}
            .container{{display:grid;grid-template-columns: 2.2fr 1fr 0.8fr;gap:50px;padding:50px 5%}}
        </style></head><body>
            <header><a href='#' class='logo'><img src='{FAVICON_DATA}' width='65'>BROKENOMORE</a><div style='text-align:right;color:#fbbf24;font-weight:900'>LIVE TERMINAL ACTIVE</div></header>
            <div class='container'>
                <div><a href='./{hero['p']}' style='color:#fff;text-decoration:none'><img src='{hero['img']}' style='width:100%;height:520px;object-fit:cover;margin-bottom:30px'><h1 style='font-size:65px;line-height:0.9;margin:0;letter-spacing:-4px;font-weight:900'>{hero['t']}</h1></a></div>
                <div style='border-left:1px solid #222;padding-left:40px'><h2 style='color:#fbbf24;font-size:13px;text-transform:uppercase;letter-spacing:3px;border-bottom:1px solid #333;padding-bottom:15px'>Intelligence Grid</h2>{grid_html}</div>
                <div style='border-left:1px solid #222;padding-left:40px'><h2 style='color:#fbbf24;font-size:13px;text-transform:uppercase;letter-spacing:3px;border-bottom:1px solid #333;padding-bottom:15px'>Global Feed</h2><ul>{feed_html}</ul></div>
            </div>
            <div style='position:fixed;bottom:0;width:100%;background:#fbbf24;color:#000;padding:10px;font-weight:900;font-size:13px;z-index:999'><marquee>BNM TERMINAL V4.0 // DEEP CORE ANALYSIS // TRADINGVIEW SYNCED // NO IMAGE ERRORS</marquee></div>
        </body></html>
        """
        with open('index.html', 'w', encoding='utf-8') as f: f.write(index_html)

if __name__ == "__main__":
    BrokenNoMoreTerminal().run()
