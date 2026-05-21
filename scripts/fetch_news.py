#!/usr/bin/env python3
"""
L&T CMMB Daily Intelligence Feed Fetcher
Fetches live infrastructure news from multiple RSS sources
and saves to data/news.json for the dashboard to consume.
"""

import json
import os
import feedparser
import requests
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))

RSS_FEEDS = [
    {
        "url": "https://news.google.com/rss/search?q=NHAI+highway+tender+awarded+India&hl=en-IN&gl=IN&ceid=IN:en",
        "type": "highways",
        "label": "NHAI / Highways"
    },
    {
        "url": "https://news.google.com/rss/search?q=coal+india+mining+contract+excavator+india&hl=en-IN&gl=IN&ceid=IN:en",
        "type": "mining",
        "label": "Mining / Coal India"
    },
    {
        "url": "https://news.google.com/rss/search?q=india+infrastructure+construction+contract+tender&hl=en-IN&gl=IN&ceid=IN:en",
        "type": "highways",
        "label": "Infrastructure"
    },
    {
        "url": "https://news.google.com/rss/search?q=DFCCIL+RVNL+railway+earthwork+contract&hl=en-IN&gl=IN&ceid=IN:en",
        "type": "railways",
        "label": "Railways"
    },
    {
        "url": "https://news.google.com/rss/search?q=metro+rail+underground+excavation+india&hl=en-IN&gl=IN&ceid=IN:en",
        "type": "metro",
        "label": "Metro"
    },
    {
        "url": "https://news.google.com/rss/search?q=L%26T+construction+order+win+infrastructure&hl=en-IN&gl=IN&ceid=IN:en",
        "type": "corporate",
        "label": "Corporate / L&T"
    }
]

def time_ago(pub_date_str):
    try:
        import email.utils
        parsed = email.utils.parsedate_to_datetime(pub_date_str)
        now = datetime.now(timezone.utc)
        diff = now - parsed.astimezone(timezone.utc)
        hours = int(diff.total_seconds() / 3600)
        if hours < 1:
            return "Just now"
        elif hours < 24:
            return f"{hours} hours ago"
        else:
            days = hours // 24
            return f"{days} day{'s' if days > 1 else ''} ago"
    except:
        return "Recent"

def clean_html(text):
    import re
    if not text:
        return ""
    text = re.sub('<[^>]+>', '', text)
    text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&nbsp;', ' ').replace('&#39;', "'").replace('&quot;', '"')
    return text.strip()[:200]

def fetch_news():
    all_news = []
    seen_titles = set()

    for feed_config in RSS_FEEDS:
        try:
            print(f"Fetching: {feed_config['label']} ...")
            feed = feedparser.parse(feed_config["url"])
            
            for entry in feed.entries[:5]:
                title = clean_html(entry.get("title", ""))
                if not title or title in seen_titles:
                    continue
                seen_titles.add(title)
                
                desc = clean_html(entry.get("summary", entry.get("description", "")))
                if len(desc) > 180:
                    desc = desc[:177] + "..."
                
                pub_date = entry.get("published", "")
                
                news_item = {
                    "title": title,
                    "desc": desc,
                    "src": entry.get("author", feed_config["label"]),
                    "time": time_ago(pub_date),
                    "link": entry.get("link", "#"),
                    "type": feed_config["type"],
                    "published": pub_date
                }
                all_news.append(news_item)
                
        except Exception as e:
            print(f"Error fetching {feed_config['label']}: {e}")

    return all_news[:20]  # Return top 20 items

def save_data(news_items):
    os.makedirs("data", exist_ok=True)
    
    # Save news
    with open("data/news.json", "w", encoding="utf-8") as f:
        json.dump(news_items, f, ensure_ascii=False, indent=2)
    
    # Save meta
    meta = {
        "last_updated": datetime.now(IST).strftime("%Y-%m-%d %H:%M IST"),
        "last_updated_utc": datetime.now(timezone.utc).isoformat(),
        "news_count": len(news_items),
        "data_sources": [f["label"] for f in RSS_FEEDS]
    }
    with open("data/meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Saved {len(news_items)} news items")
    print(f"✅ Last updated: {meta['last_updated']}")

if __name__ == "__main__":
    print("🚀 L&T CMMB Intelligence Feed Fetcher")
    print("=" * 50)
    news = fetch_news()
    if news:
        save_data(news)
    else:
        print("⚠️  No news fetched — keeping existing data")
