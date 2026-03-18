# -*- coding: utf-8 -*-
import google.generativeai as genai
import subprocess
import datetime
import os
import sys
import requests
import json
from xml.etree import ElementTree

api_key = os.environ.get("GEMINI_API_KEY")
fss_auth_key = os.environ.get("FSS_AUTH_KEY", "")
if not api_key:
    sys.exit(1)

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.5-flash")

date_obj = datetime.date.today()
today = str(date_obj)
year = date_obj.year
month = date_obj.month

last_monday = date_obj - datetime.timedelta(days=date_obj.weekday() + 7)
last_sunday = last_monday + datetime.timedelta(days=6)
week_num = (last_monday.day - 1) // 7 + 1

date_range = str(last_monday) + " ~ " + str(last_sunday)
week_label = str(year) + "년 " + str(month) + "월 " + str(week_num) + "주차"
month_label = str(year) + "년" + str(month) + "월"

headers = {"User-Agent": "Mozilla/5.0 (compatible; HanAI-Bot/1.0)"}
collected = []

# FSS Open API
try:
    fss_url = (
        "https://www.fss.or.kr/fss/kr/openApi/api/bodoInfo.jsp"
        "?apiType=json"
        "&startDate=" + str(last_monday) +
        "&endDate=" + str(last_sunday) +
        "&authKey=" + fss_auth_key
    )
    res = requests.get(fss_url, headers=headers, timeout=10)
    data = res.json()
    items = data.get("reponse", {}).get("result", [])
    lines = ["[FSS] " + str(len(items)) + " items found"]
    for item in items[:10]:
        lines.append(
            "title: " + str(item.get("subject", "")) +
            " | date: " + str(item.get("regDate", "")) +
            " | url: " + str(item.get("originUrl", "")) +
            " | org: " + str(item.get("publishOrg", ""))
        )
    collected.append("\n".join(lines))
except Exception as e:
    collected.append("FSS API failed: " + str(e))

# FSC RSS feeds
fsc_feeds = [
    ("FSC-press", "http://www.fsc.go.kr/about/fsc_bbs_rss/?fid=0111"),
    ("FSC-explain", "http://www.fsc.go.kr/about/fsc_bbs_rss/?fid=0112"),
    ("FSC-notice", "http://www.fsc.go.kr/about/fsc_bbs_rss/?fid=0114"),
]

for feed_name, feed_url in fsc_feeds:
    try:
        res = requests.get(feed_url, headers=headers, timeout=10)
        res.encoding = "utf-8"
        root = ElementTree.fromstring(res.content)
        items = root.findall(".//item")
        lines = [feed_name + ": " + str(len(items)) + " items"]
        for item in items[:10]:
            t = item.find("title")
            l = item.find("link")
            d = item.find("pubDate")
            if t is None:
                continue
            lines.append(
                "title: " + (t.text or "") +
                " | date: " + (d.text if d is not None else "") +
                " | url: " + (l.text if l is not None else "")
            )
        collected.append("\n".join(lines))
    except Exception as e:
        collected.append(feed_name + " failed: " + str(e))

# FSC 금융위의결 / 증선위의결
fsc_pages = [
    ("FSC-committee", "https://www.fsc.go.kr/no020101"),
    ("FSC-sec-committee", "https://www.fsc.go.kr/no020102"),
]
for page_name, page_url in fsc_pages:
    try:
        res = requests.get(page_url, headers=headers, timeout=10)
        res.encoding = "utf-8"
        text = res.text[:3000]
        collected.append(page_name + " raw:\n" + text)
    except Exception as e:
        collected.append(page_name + " failed: " + str(e))

raw_data = "\n\n".join(collected)

prompt_lines = [
    "Today: " + today,
    "Report period: " + date_range + " (" + week_label + ")",
    "",
    "Below is REAL data from official Korean financial regulation websites.",
    "Write a report ONLY based on this data. Do NOT invent information.",
    "If no real data exists for a section, write: " + chr(54644) + chr(45817) + " " + chr(44592) + chr(44036) + " " + chr(45236) + " " + chr(48320) + chr(44221) + chr(49324) + chr(54637) + " " + chr(50630) + chr(51020),
    "",
    "=== REAL DATA ===",
    raw_data,
    "=================",
    "",
    "Write Korean report:",
    "",
    "## " + week_label + " (" + date_range + ") " + chr(44552) + chr(50928) + chr(44508) + chr(51221) " " + chr(48320) + chr(44221) + chr(49324) + chr(54637) + " " + chr(48270) + chr(47532) + chr(54595) + chr(44536),
    "",
    "### 1. K-IFRS " + chr(44060) + chr(51221) + " " + chr(48120) + chr(54644) + chr(49437) + chr(49436),
    "### 2. FSS " + chr(44048) + chr(47532) + " " + chr(51648) + chr(52840) + " " + chr(48143) " " + chr(44277) + chr(49884),
    "### 3. FSC " + chr(44552) + chr(50856) + chr(50948) + chr(50896) + chr(54924) + " " + chr(51452) + chr(50836) + " " + chr(48156) + chr(54364),
    "### 4. FSC " + chr(44552) + chr(50856) + chr(50948) + chr(51032) + chr(44208) + " / " + chr(51613) + chr(49440) + chr(50948) + chr(51032) + chr(44208),
    "### 5. KICPA " + chr(44277) + chr(51648),
    "### 6. " + chr(44148) + chr(49444) + " " + chr(48512) + chr(46041) + chr(49328) + " " + chr(44508) + chr(51221) + " " + chr(48320) + chr(44221),
    "### 7. " + chr(44048) + chr(47532) + " " + chr(51312) + chr(52824) + " " + chr(49324) + chr(47840),
    "",
    "Rules:",
    "Write all content in Korean.",
    "Use exact dates: org + 'is YYYY MM DD' + announced.",
    "Only include real URLs from the data above.",
    "Mark urgent items with [" + chr(44553) + chr(44553) + "]",
    "End with 3 practical notes for accountants.",
]

prompt = "\n".join(prompt_lines)

response = model.generate_content(prompt)
report = response.text
title = "[" + chr(51452) + chr(44036) + chr(48270) + chr(47532) + chr(54595) + chr(44536) + "] " + week_label + " (" + date_range + ")"

with open("/tmp/report_title.txt", "w", encoding="utf-8") as f:
    f.write(title)

with open("/tmp/report_body.txt", "w", encoding="utf-8") as f:
    f.write(report)

subprocess.run(
    ["gh", "label", "create", month_label,
     "--color", "0075ca",
     "--description", month_label],
    capture_output=True, text=True
)

result = subprocess.run(
    ["gh", "issue", "create",
     "--title", title,
     "--body", report,
     "--label", month_label],
    capture_output=True, text=True
)

if result.returncode == 0:
    print("Done:", title)
else:
    print("Failed:", result.stderr)
    sys.exit(1)
```

---

## 📄 gemini-finance-monitor.yml — FSS_AUTH_KEY 추가
```
github.com/tojidi-debug/HanAI/edit/main/.github/workflows/gemini-finance-monitor.yml
