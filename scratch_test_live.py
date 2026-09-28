import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import json
import sys

# Ensure UTF-8 output encoding
sys.stdout.reconfigure(encoding='utf-8')

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
query = '"Backend Engineer" OR "Data Engineer" OR "AI Engineer" Bengaluru OR Hyderabad Python'
rss_url = f"https://news.google.com/rss/search?q={urllib.parse.quote(query)}&hl=en-IN&gl=IN&ceid=IN:en"

req = urllib.request.Request(rss_url, headers=headers)
with urllib.request.urlopen(req, timeout=10) as resp:
    xml_data = resp.read().decode('utf-8')
    root = ET.fromstring(xml_data)
    items = root.findall('.//item')
    print(f"Google RSS returned {len(items)} items:")
    for item in items[:10]:
        title = item.find('title').text if item.find('title') is not None else ""
        link = item.find('link').text if item.find('link') is not None else ""
        pubDate = item.find('pubDate').text if item.find('pubDate') is not None else ""
        print(f"• {title}\n  Date: {pubDate}\n  Link: {link}\n")
