import google.generativeai as genai
import subprocess
import datetime
import os
import sys

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    sys.exit(1)

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.5-pro")

today = str(datetime.date.today())

prompt = "today: " + today + "\n"
prompt += "You are a Korean accounting expert.\n"
prompt += "Summarize changes from the past week in Korean.\n"
prompt += "1. K-IFRS revision\n"
prompt += "2. FSS audit guidelines\n"
prompt += "3. KICPA announcements\n"
prompt += "4. External Audit Act changes\n"
prompt += "5. IASB/FASB updates\n"
prompt += "6. Construction revenue recognition\n"
prompt += "7. Real estate presale accounting\n"
prompt += "8. PF project financing\n"
prompt += "9. Construction cost audit issues\n"
prompt += "10. Real estate asset revaluation\n"
prompt += "11. Recent enforcement actions\n"
prompt += "Mark urgent items with URGENT\n"
prompt += "End with 3 practical notes.\n"

response = model.generate_content(prompt)
report = response.text
title = "[Weekly Brief] " + today

result = subprocess.run(
    ["gh", "issue", "create", "--title", title, "--body", report],
    capture_output=True,
    text=True
)

if result.returncode == 0:
    print("Done")
else:
    print(result.stderr)
    sys.exit(1)
