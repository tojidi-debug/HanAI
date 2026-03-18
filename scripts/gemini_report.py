import google.generativeai as genai
import subprocess
import datetime
import os
import sys
import requests
from xml.etree import ElementTree

api_key = os.environ.get("GEMINI_API_KEY")
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

RSS_SOURCES = [
    ("금융감독원", "https://www.fss.or.kr/fss/rss/pressReleaseRss.jsp"),
    ("금융위원회", "https://www.fsc.go.kr/rss/rssList.do?bbsid=BBS0048"),
    ("회계기준원", "https://www.kasb.or.kr/rss/news.do"),
    ("한국공인회계사회", "https://www.kicpa.or.kr/rss/news.do"),
]

headers = {
    "User-Agent": "Mozilla/5.0 (compatible; HanAI-Bot/1.0)"
}

collected = []

for org_name, rss_url in RSS_SOURCES:
    try:
        res = requests.get(rss_url, headers=headers, timeout=10)
        res.encoding = "utf-8"
        root = ElementTree.fromstring(res.content)

        items = root.findall(".//item")
        org_items = []

        for item in items[:20]:
            title_el = item.find("title")
            link_el = item.find("link")
            date_el = item.find("pubDate")
            desc_el = item.find("description")

            if title_el is None:
                continue

            item_title = title_el.text or ""
            item_link = link_el.text if link_el is not None else ""
            item_date = date_el.text if date_el is not None else ""
            item_desc = desc_el.text if desc_el is not None else ""

            org_items.append(
                "[" + org_name + "] " + item_title +
                " | 날짜: " + item_date +
                " | 링크: " + item_link +
                " | 내용: " + item_desc[:200]
            )

        if org_items:
            collected.append(org_name + " 최신 공지:\n" + "\n".join(org_items))
        else:
            collected.append(org_name + ": 최신 공지 없음")

    except Exception as e:
        collected.append(org_name + ": 데이터 수집 실패 (" + str(e) + ")")

raw_data = "\n\n".join(collected)

prompt = "오늘: " + today + "\n"
prompt += "보고 기간: " + date_range + " (" + week_label + ")\n\n"
prompt += "아래는 " + date_range + " 기간에 수집된 실제 공식 기관 공지사항입니다.\n"
prompt += "이 데이터만을 기반으로 보고서를 작성하세요.\n"
prompt += "데이터에 없는 내용은 절대 추가하지 마세요.\n\n"
prompt += "=== 수집된 실제 데이터 ===\n"
prompt += raw_data + "\n"
prompt += "=========================\n\n"
prompt += "위 실제 데이터를 바탕으로 한국어 보고서를 작성하세요:\n\n"
prompt += "## " + week_label + " (" + date_range + ") 금융규정 변경사항 브리핑\n\n"
prompt += "### 1. K-IFRS 개정 및 해석서 (회계기준원)\n"
prompt += "### 2. 금융감독원 감리 지침 및 공시\n"
prompt += "### 3. 금융위원회 주요 발표\n"
prompt += "### 4. 한국공인회계사회(KICPA) 공지\n
