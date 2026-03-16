from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import re
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_FILE = "CS_Leaders_기출문제_DB.json"

class UserRequest(BaseModel):
    user_query: str

@app.post("/ask_ai")
async def get_answer(request: UserRequest):
    if not os.path.exists(DB_FILE):
        return {"answer": "⚠️ 서버 오류: DB 파일을 찾을 수 없습니다."}

    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            question_db = json.load(f)
    except Exception as e:
        return {"answer": f"⚠️ 파일 읽기 오류: {str(e)}"}

    query = request.user_query.strip()
    keywords = re.findall(r'[가-힣a-zA-Z0-9]{2,}', query)
    
    results = []
    for item in question_db:
        content = item.get("문제내용_및_보기", "") + item.get("해설_및_Tip", "")
        score = sum(1 for kw in keywords if kw in content)
        
        if score > 0:
            # 기출연도(예: 2024.06)에서 숫자만 추출하여 정렬 기준으로 활용
            year_val = item.get("기출연도", "0000.00")
            results.append({
                "score": score,
                "year": year_val,
                "data": item
            })

    if not results:
        return {"answer": "죄송합니다. 관련 기출 데이터를 찾지 못했습니다."}

    # [핵심 수정] 1순위: 키워드 점수 높은 순, 2순위: 기출연도 최신순으로 정렬
    results.sort(key=lambda x: (x['score'], x['year']), reverse=True)

    # 가장 최신이면서 유사도가 높은 상위 문제 추출
    top_res = results[0]['data']
    
    return {
        "answer": f"🎯 [최신 출제 패턴] 검색 결과입니다!\n\n"
                  f"📌 출제: {top_res['과목']} ({top_res['기출연도']})\n"
                  f"📝 문제: {top_res['문제내용_및_보기']}\n\n"
                  f"💡 분석 Tip: {top_res['해설_및_Tip']}\n"
                  f"📍 정답: {top_res['정답']}번\n\n"
                  f"📢 최신 기출을 중심으로 반복되는 키워드를 꼭 확인하세요!"
    }