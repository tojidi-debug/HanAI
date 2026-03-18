# -*- coding: utf-8 -*-
import subprocess
import datetime
import os
import sys
import requests
import json
from xml.etree import ElementTree
from google import genai

api_key = os.environ.get("GEMINI_API_KEY")
fss_auth_key = os.environ.get("FSS_AUTH_KEY", "")
if not api_key:
    sys.exit(1)

client = genai.Client(api_key=api_key)

script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, "config.json")
with open(config_path, "r", encoding="utf-8") as f:
    cfg = json.load(f)

date_obj = datetime.date.today()
today = str(date_obj)
year = date_obj.year
month = date_obj.month

last_monday = date_obj - datetime.timedelta(days=date_obj.weekday() + 7)
last_sunday = last_monday + datetime.timedelta(days=6)
week_num = (last_monday.day - 1) // 7 + 1

date_range = str(last_monday) + " ~ " + str(last_sunday)
week_label = (
    str(year) + cfg["year_suffix"] +
    str(month) + cfg["month_suffix"] +
    str(week_num) + cfg["week_label_suffix"]
)
month_label = str(year) + cfg["month_label_year"] + str(month) + cfg["month_label_month"]

headers = {"User-Agent": "Mozilla/5.0 (compatible; HanAI-Bot/1.0)"}
collected = []

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
    lines = ["[FSS] " + str(len(items)) + " items"]
    for item in items[:10]:
        lines.append(
            "title: " + str(item.get("subject", "")) +
            " | date: " + str(item.get("regDate", "")) +
            " | url: " + str(item.get("originUrl", ""))
        )
    collected.append("\n".join(lines))
except Exception as e:
    collected.append("FSS failed: " + str(e))

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

fsc_pages = [
    ("FSC-committee", "https://www.fsc.go.kr/no020101"),
    ("FSC-sec", "https://www.fsc.go.kr/no020102"),
]
for page_name, page_url in fsc_pages:
    try:
        res = requests.get(page_url, headers=headers, timeout=10)
        res.encoding = "utf-8"
        collected.append(page_name + ":\n" + res.text[:2000])
    except Exception as e:
        collected.append(page_name + " failed: " + str(e))

raw_data = "\n\n".join(collected)

sections = "\n".join([
    cfg["s1"], cfg["s2"], cfg["s3"], cfg["s4"],
    cfg["s5"], cfg["s6"], cfg["s7"]
])
rules = "\n".join([
    cfg["r1"], cfg["r2"], cfg["r3"], cfg["r4"], cfg["r5"]
])

prompt = (
    "Today: " + today + "\n"
    "Report period: " + date_range + " (" + week_label + ")\n\n"
    "Below is REAL data from official Korean financial regulation websites.\n"
    "Write report ONLY based on this data. Do NOT invent anything.\n"
    "If no data for a section, write: " + cfg["no_data"] + "\n\n"
    "=== REAL DATA ===\n" +
    raw_data + "\n"
    "=================\n\n"
    "Write Korean report:\n\n"
    "## " + week_label + " (" + date_range + ") " + cfg["report_header"] + "\n\n" +
    sections + "\n\n"
    "Rules:\n" + rules
)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt
)

report = response.text
title = cfg["title_prefix"] + " " + week_label + " (" + date_range + ")"

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
