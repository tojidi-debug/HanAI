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
month_label = str(year) + "년" + str(month) + "월"

prompt = "today: " + today + "\n"
prompt += "Report period: " + date_range + " (" + week_label + ")\n"
prompt += "You are a Korean accounting and financial regulation expert.\n"
prompt += "Summarize major changes from " + date_range + " in Korean.\n"
prompt += "IMPORTANT: For each item, include actual source URLs as markdown hyperlinks.\n"
prompt += "Format each source like this: [출처: 기관명](https://actual-url.com)\n"
prompt += "Start the report with this header: ## " + week_label + " (" + date_range + ") 금융규정 변경사항 브리핑\n"
prompt += "1. K-IFRS revision or interpretation\n"
prompt += "2. FSS audit guidelines - fss.or.kr\n"
prompt += "3. KICPA announcements - kicpa.or.kr\n"
prompt += "4. External Audit Act changes\n"
prompt += "5. IASB/FASB updates\n"
prompt += "6. Construction revenue recognition changes\n"
prompt += "7. Real estate presale accounting changes\n"
prompt += "8. PF project financing supervision\n"
prompt += "9. Construction cost audit issues\n"
prompt += "10. Real estate asset revaluation\n"
prompt += "11. Recent enforcement actions - fss.or.kr\n"
prompt += "Rules: Write in Korean. Mark urgent items with [긴급]. "
prompt += "No changes: 이번 주 해당 없음. "
prompt += "End with 3 practical notes for accountants.\n"

response = model.generate_content(prompt)
report = response.text
title = "[주간브리핑] " + week_label + " (" + date_range + ") 금융규정 변경사항"

with open("/tmp/report_title.txt", "w") as f:
    f.write(title)

with open("/tmp/report_body.txt", "w") as f:
    f.write(report)

subprocess.run(
    ["gh", "label", "create", month_label,
     "--color", "0075ca",
     "--description", month_label + " 금융규정 브리핑"],
    capture_output=True,
    text=True
)

result = subprocess.run(
    ["gh", "issue", "create",
     "--title", title,
     "--body", report,
     "--label", month_label],
    capture_output=True,
    text=True
)

if result.returncode == 0:
    print("Done:", title)
else:
    print("Failed:", result.stderr)
    sys.exit(1)
