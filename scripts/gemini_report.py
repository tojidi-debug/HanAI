import google.generativeai as genai
import subprocess
import datetime
import os
import sys

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

prompt = "today: " + today + "\n"
prompt += "Report period: " + date_range + " (" + week_label + ")\n"
prompt += "You are a Korean accounting and financial regulation expert.\n"
prompt += "Summarize major changes from " + date_range + " in Korean.\n"
prompt += "IMPORTANT: For each item, include actual source URLs as markdown hyperlinks.\n"
prompt += "Format each source like this: [출처: 기관명](https://actual-url.com)\n"
prompt += "IMPORTANT: Start the report with this exact header:\n"
prompt += "## " + week_label + " (" + date_range + ") 금융규정 변경사항 브리핑\n\n"
prompt += "1. K-IFRS revision or interpretation - check iasb.org, kasb.or.kr\n"
prompt += "2. FSS audit guidelines - check fss.or.kr\n"
prompt += "3. KICPA announcements - check kicpa.or.kr\n"
prompt += "4. External Audit Act changes - check moleg.go.kr, fss.or.kr\n"
prompt += "5. IASB/FASB updates - check iasb.org, fasb.org\n"
prompt += "6. Construction revenue recognition changes\n"
prompt += "7. Real estate presale accounting changes\n"
prompt += "8. PF project financing supervision - check fss.or.kr\n"
prompt += "9. Construction cost audit issues\n"
prompt += "10. Real estate asset revaluation\n"
prompt += "11. Recent enforcement actions - check fss.or.kr, krx.co.kr\n\n"
prompt += "Rules:\n"
prompt += "- Write all content in Korean\n"
prompt += "- Mark urgent items with [긴급]\n"
prompt += "- Items with no changes: 이번 주 해당 없음\n"
prompt += "- Each item MUST end with at least one source hyperlink\n"
prompt += "- End with 3 practical notes for accountants\n"

response = model.generate_content(prompt)
report = response.text
title = "[주간브리핑] " + week_label + " (" + date_range + ") 금융규정 변경사항"

result = subprocess.run(
    ["gh", "issue", "create", "--title", title, "--body", report],
    capture_output=True,
    text=True
)

if result.returncode == 0:
    print("Done:", title)
else:
    print("Failed:", result.stderr)
    sys.exit(1)
```

---

## 결과 예시
```
Issue 제목:
[주간브리핑] 2026년 3월 2주차 (2026-03-09 ~ 2026-03-15) 금융규정 변경사항

본문 상단:
## 2026년 3월 2주차 (2026-03-09 ~ 2026-03-15) 금융규정 변경사항 브리핑
