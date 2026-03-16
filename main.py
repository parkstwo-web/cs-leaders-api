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

# 파일 이름을 변수로 고정 (선생님이 알려주신 이름)
DB_FILE = "CS_Leaders_기출문제_DB.json"

class UserRequest(BaseModel):
    user_query: str

@app.post("/ask_ai")
async def get_answer(request: UserRequest):
    # 1. 파일 존재 여부 먼저 확인
    if not os.path.exists(DB_FILE):
        return {"answer": f"⚠️ 서버 오류: {DB_FILE} 파일을 찾을 수 없습니다. 깃허브 업로드 상태를 확인해주세요."}

    # 2. 파일 읽기
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            question_db = json.load(f)
    except Exception as e:
        return {"answer": f"⚠️ 파일 읽기 오류: {str(e)}"}

    query = request.user_query.strip()
    # 핵심 단어 추출 (한글/영문 2글자 이상)
    keywords = re.findall(r'[가-힣a-zA-Z0-9]{2,}', query)
    
    results = []
    for item in question_db:
        content = item.get("문제내용_및_보기", "") + item.get("해설_및_Tip", "")
        # 입력된 단어들이 문제에 얼마나 포함되었는지 점수화
        score = sum(1 for kw in keywords if kw in content)
        if score > 0:
            results.append((score, item))

    # 가장 많이 겹친 순서로 정렬
    results.sort(key=lambda x: x[0], reverse=True)

    if not results:
        return {"answer": "죄송합니다. 106회차 DB에서 관련 내용을 찾지 못했습니다. 핵심 키워드 위주로 질문해 주세요."}

    # 가장 유사한 1순위 문제 출력
    res = results[0][1]
    return {"answer": f"🎯 검색 결과입니다!\n\n[출제] {res['과목']} ({res['기출연도']})\n[문제] {res['문제내용_및_보기']}\n\n💡 분석 Tip: {res['해설_및_Tip']}\n📍 정답: {res['정답']}번"}