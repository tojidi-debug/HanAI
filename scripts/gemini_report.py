import google.generativeai as genai
import subprocess
import datetime
import os
import sys

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("ERROR: GEMINI_API_KEY")
    sys.exit(1)

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-pro')

today = str(datetime.date.today())

prompt = "today: " + today + "\n"
prompt += "You are a Korean accounting and financial regulation expert.\n"
prompt += "Summarize major changes from the past week in Korean.\n\n"
prompt += "1. K-IFRS revision or interpretation\n"
prompt += "2. FSS audit guidelines changes\n"
prompt += "3. KICPA announcements\n"
prompt += "4. External Audit Act changes\n"
prompt += "5. IASB/FASB updates affecting Korea\n"
prompt += "6. Construction revenue recognition changes\n"
prompt += "7. Real estate presale accounting changes\n"
prompt += "8. PF project financing supervision\n"
prompt += "9. Construction cost ratio audit issues\n"
prompt += "10. Real estate asset revaluation\n"
prompt += "11. Recent enforcement actions\n\n"
prompt += "Format: number each item, mark urgent items with [URGENT]\n"
prompt += "End with 3 practical notes for accountants.\n"

print("Calling Gemini API...")
response = model.generate_content(prompt)
report = response.text
title = "[Weekly Brief] " + today

print("Creating GitHub Issue...")
result = subprocess.run(
    ['gh', 'issue', 'create', '--title', title, '--body', report],
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

## 이번 변경점
```
한국어 주석 전부 제거
특수문자 전부 제거
영문만 사용 (Gemini가 한국어로 답변하도록 프롬프트에 명시)
