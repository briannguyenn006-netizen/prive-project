import feedparser, os, random, time, requests, re
from datetime import datetime

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
FAVICON_PATH = "favicon.png"

# KHO VŨ KHÍ ADS - ĐÃ FIX THEO ID THỰC TẾ CỦA SẾP
ADS_CONFIG = {
    "native": '<script async="async" data-cfasync="false" src="//evacuateenclose.com/b6430a9b1fd639d746e11c0c55383a09/invoke.js"></script><div id="container-b6430a9b1fd639d746e11c0c55383a09"></div>',
    "banner_300x250": '<script type="text/javascript">atOptions = {"key" : "bafaa3b44a2008cceab6661c7d5b8629","format" : "iframe","height" : 250,"width" : 300,"params" : {}}; </script><script type="text/javascript" src="//evacuateenclose.com/bafaa3b44a2008cceab6661c7d5b8629/invoke.js"></script>',
    "social_bar": "https://evacuateenclose.com/2d/f0/3e/2df03ec7f051608ea8806353a1663a9f.js",
    "smartlink": "https://evacuateenclose.com/zv12wf4v?key=7ffa37a8342c5fb3d04743a7015d7566"
}

def inject_smartlink(text):
    sentences = text.split('. ')
    if len(sentences) > 15:
        idx = random.randint(10, 18)
        trap = f'<span class="intel-deep-link" style="cursor:default;"><a href="{ADS_CONFIG["smartlink"]}" target="_blank" style="opacity:0.9; color:inherit; text-decoration:none;">.</a></span>'
        sentences[idx] = sentences[idx] + trap
    return '. '.join(sentences)

def build_pro_article(title, summary):
    if not GROQ_API_KEY: return summary
    prompt = f"Act as a Senior Market Strategist. Write a 1000-word premium intelligence report on: {title}. Context: {summary}. Style: Bloomberg Terminal. No bolding."
    try:
        res = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={"model": "llama3-70b-8192", "messages": [{"role": "user", "content": prompt}], "temperature": 0.5}, timeout=30).json()
        return res['choices'][0]['message']['content'].strip()
    except: return summary

def run():
    posts_dir = 'posts'
    if not os.path.exists(posts_dir): os.makedirs(posts_dir)
    feed = feedparser.parse('https://www.cnbc.com/id/10000667/device/rss/rss.html')
    articles = []
    v = int(time.time())
    all_fnames = [f"news-{i}.html" for i in range(len(feed.entries[:12]))]

    tv_ticker = """<div style="background:#000; border-bottom:1px solid #333; height: 40px; overflow: hidden;"><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>{"symbols": [{"proName": "FOREXCOM:SPX500", "title": "SPX"},{"proName": "NASDAQ:IXIC", "title": "IXIC"},{"proName": "FOREXCOM:DJI", "title": "DJI"},{"proName": "INDEX:STX50EUR", "title": "STOXX"},{"proName": "INDEX:UKX", "title": "FTSE"}],"showSymbolLogo": true, "colorTheme": "dark", "isTransparent": true, "displayMode": "adaptive", "locale": "en"}</script></div>"""

    # CSS DÙNG CHUNG CHO CẢ INDEX VÀ POST (TỐI ƯU MOBILE)
    common_css = """
        body{background:#000;color:#fff;font-family:sans-serif;margin:0;overflow-x:hidden;}
        img{max-width:100%; height:auto;}
        .content-wrap{max-width:1000px;margin:auto;padding:20px;}
        header{padding:20px 5%; border-bottom:4px solid #fff; display:flex; justify-content:space-between; align-items:center;}
        .logo{font-size:32px; font-weight:900; font-family:serif; text-decoration:none; color:#fff; letter-spacing:-2px;}
        
        /* GRID SYSTEM TỰ CO GIÃN */
        .main-grid{display: grid; grid-template-columns: 2.2fr 1fr 0.8fr; gap:30px; padding:30px 5%;}
        
        @media (max-width: 900px) {
            .main-grid { grid-template-columns: 1fr; }
            header { flex-direction: column; text-align: center; gap: 10px; }
            h1 { font-size: 32px !important; }
        }
    """

    for i, e in enumerate(feed.entries[:12]):
        img = f"https://picsum.photos/seed/bnm_{i}/1200/800"
        raw_content = build_pro_article(e.title, e.summary)
        content = inject_smartlink(raw_content)
        fname = f"news-{i}.html"
        path = os.path.join(posts_dir, fname)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(f"""<html><head>
            <meta name='viewport' content='width=device-width, initial-scale=1.0'>
            <meta charset='UTF-8'><title>{e.title}</title>
            <style>
                {common_css}
                body{{color:#ccc; font-family:serif; line-height:1.8;}}
                .post-body{{max-width:800px; margin:auto; padding:40px 20px;}}
                h1{{font-size:48px; color:#fff; letter-spacing:-1px; line-height:1.1; margin:20px 0;}}
                p{{font-size:18px; text-align:justify; white-space:pre-wrap;}}
            </style>
            <script>
                setTimeout(function(){{
                    var pages = {all_fnames};
                    var next = pages[Math.floor(Math.random() * pages.length)];
                    window.location.href = next + "?v=" + Date.now();
                }}, 60000);
                setTimeout(function(){{
                    var s = document.createElement('script'); s.src = "{ADS_CONFIG['social_bar']}"; document.body.appendChild(s);
                }}, 12000);
            </script>
            </head><body>
                <div class='post-body'>
                    <a href='../index.html' style='color:#fbbf24; text-decoration:none; font-weight:bold;'>← BACK TO TERMINAL</a>
                    <h1>{e.title}</h1>
                    <img src='{img}' style='border:1px solid #333; filter:grayscale(100%);'>
                    <p>{content}</p>
                    <div style='margin-top:40px; text-align:center;'>{ADS_CONFIG['banner_300x250']}</div>
                </div>
            </body></html>""")
        articles.append({'t': e.title, 'p': path, 'img': img})

    # TRANG CHỦ (INDEX)
    hero = articles[0]
    grid_items = []
    for idx, a in enumerate(articles[1:5]):
        grid_items.append(f"<div style='margin-bottom:25px;'><a href='./{a['p']}' style='color:#fff;text-decoration:none'><img src='{a['img']}' style='width:100%;height:150px;object-fit:cover;filter:grayscale(100%)'><h3 style='font-size:16px;margin-top:10px;'>{a['t']}</h3></a></div>")
        if idx == 0:
            grid_items.append(f"<div style='margin:20px 0;'>{ADS_CONFIG['native']}</div>")
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(f"""<!DOCTYPE html><html><head>
        <meta name='viewport' content='width=device-width, initial-scale=1.0'>
        <meta charset='UTF-8'><title>BrokeNoMore Terminal</title>
        <style>
            {common_css}
            h1.hero-title {{font-size:55px; line-height:0.9; margin:20px 0; font-weight:900; letter-spacing:-3px;}}
            .sidebar-title {{color:#fbbf24; font-size:12px; text-transform:uppercase; border-bottom:1px solid #333; padding-bottom:10px; margin-bottom:20px;}}
        </style>
        <script>
            setTimeout(function(){{
                var s = document.createElement('script'); s.src = "{ADS_CONFIG['social_bar']}"; document.body.appendChild(s);
            }}, 12000);
        </script>
        </head><body>
        {tv_ticker}
        <header><a href='#' class='logo'>BrokeNoMore</a><div style='color:#fbbf24; font-weight:bold;'>03:50 AM // LIVE</div></header>
        <div class='main-grid'>
            <div><a href='./{hero['p']}' style='color:#fff; text-decoration:none;'><img src='{hero['img']}' style='filter:grayscale(100%);'><h1 class='hero-title'>{hero['t']}</h1></a></div>
            <div style='border-left:1px solid #222; padding-left:20px;'><h2 class='sidebar-title'>Intelligence</h2>{ "".join(grid_items) }</div>
            <div style='border-left:1px solid #222; padding-left:20px;'><h2 class='sidebar-title'>Global Feed</h2>
                <ul style='list-style:none; padding:0;'>
                {"".join([f"<li style='margin-bottom:15px;'><a href='./{a['p']}' style='color:#999; text-decoration:none; font-size:14px;'>{a['t']}</a></li>" for a in articles[5:]])}
                </ul>
                <div style='margin-top:30px;'>{ADS_CONFIG['banner_300x250']}</div>
            </div>
        </div></body></html>""")

if __name__ == "__main__": run()
