import google.generativeai as genai
import subprocess
import datetime
import os
import sys

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("ERROR: GEMINI_API_KEY 없음")
    sys.exit(1)

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-pro')

today = str(datetime.date.today())

prompt = "오늘 날짜: " + today + "\n"
prompt += "당신은 한국 회계감리 및 금융감독 전문가입니다.\n"
prompt += "아래 항목에 대해 최근 1주일 내 주요 변경사항을 한국어로 요약해줘.\n\n"
prompt += "[공통 회계 감독 규정]\n"
prompt += "1. K-IFRS 개정 또는 해석서 발표\n"
prompt += "2. 금융감독원 감리 관련 공시 또는 지침 변경\n"
prompt += "3. 한국공인회계사회(KICPA) 주요 공지\n"
prompt += "4. 외감법 주기적 지정제 관련 규정 변화\n"
prompt += "5. IASB/FASB 동향 중 국내 영향 있는 것\n\n"
prompt += "[건설 부동산 업종 특화]\n"
prompt += "6. 건설업 공사수익 인식 관련 기준 변경\n"
prompt += "7. 부동산 분양 회계처리 관련 지침 변화\n"
prompt += "8. PF 프로젝트 파이낸싱 관련 금융감독 동향\n"
prompt += "9. 건설업 원가율 손실계약 충당부채 감리 이슈\n"
prompt += "10. 부동산 자산재평가 및 공정가치 측정 관련 사항\n"
prompt += "11. 건설 부동산 상장사 최근 감리 조치 사례\n\n"
prompt += "[출력 형식]\n"
prompt += "변경사항 없는 항목: 이번 주 해당 없음\n"
prompt += "각 항목은 번호와 함께 간결하게 요약\n"
prompt += "마지막에 실무 적용 시 주의사항 3줄 이내로 요약\n"
prompt += "심각도 높은 이슈는 앞에 [긴급] 표시\n"

print("Gemini API 호출 중...")
response = model.generate_content(prompt)
report = response.text
title = "[주간브리핑] 금융 건설부동산 규정 변경사항 " + today

print("GitHub Issue 생성 중...")
result = subprocess.run(
    ['gh', 'issue', 'create', '--title', title, '--body', report],
    capture_output=True,
    text=True
)

if result.returncode == 0:
    print("Issue 생성 완료:", title)
else:
    print("Issue 생성 실패:", result.stderr)
    sys.exit(1)
```

---

## 핵심 변경점
```
이전: f""" ... → ... """  ← 특수문자 포함 가능성
이후: prompt += "..."     ← 한 줄씩 더하기, 특수문자 없음
