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

lines = []
lines.append("today: " + today)
lines.append("You are a Korean accounting and financial regulation expert.")
lines.append("Summarize major changes from the past week in Korean.")
lines.append("1. K-IFRS revision or interpretation")
lines.append("2. FSS audit guidelines changes")
lines.append("3. KICPA announcements")
lines.append("4. External Audit Act changes")
lines.append("5. IASB/FASB updates affecting Korea")
lines.append("6. Construction revenue recognition changes")
lines.append("7. Real estate presale accounting changes")
lines.append("8. PF project financing supervision")
lines.append("9. Construction cost ratio audit issues")
lines.append("10. Real estate asset revaluation")
lines.append("11. Recent enforcement actions")
lines.append("Format: number each item")
lines.append("Mark urgent items with URGENT")
lines.append("End with 3 practical notes for accountants.")

prompt = "\n".join(lines)

response = model.generate_content(prompt)
report = response.text
title = "[Weekly Brief] " + today

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
