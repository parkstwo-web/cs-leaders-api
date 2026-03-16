from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB 로드
try:
    with open("CS_Leaders_기출문제_DB.json", "r", encoding="utf-8") as f:
        question_db = json.load(f)
except Exception:
    question_db = []

class UserRequest(BaseModel):
    user_query: str

@app.post("/ask_ai")
async def get_answer(request: UserRequest):
    query = request.user_query.strip()
    
    # 1. 먼저 아주 핵심적인 키워드만 추출 (3글자 이상의 단어들)
    # 문장 전체를 비교하는 대신 단어 단위로 쪼개서 검색합니다.
    keywords = [k for k in re.findall(r'[가-힣a-zA-Z0-9]{2,}', query)]
    
    results = []
    for item in question_db:
        db_content = item.get("문제내용_및_보기", "")
        db_tip = item.get("해설_및_Tip", "")
        combined = (db_content + db_tip).replace(" ", "")
        
        # 입력된 키워드 중 3개 이상이 DB 내용에 포함되어 있으면 '유사 문제'로 판단
        match_count = 0
        for kw in keywords[:10]: # 앞부분 키워드 10개만 검사
            if kw in combined:
                match_count += 1
        
        # 키워드가 많이 겹칠수록 유사도가 높은 문제임
        if match_count >= 2: 
            results.append((match_count, item))

    # 많이 겹친 순서대로 정렬
    results.sort(key=lambda x: x[0], reverse=True)

    if not results:
        return {"answer": "죄송합니다. 해당 문제와 일치하거나 유사한 기출 유형을 찾지 못했습니다. '트렌드'나 '패드'처럼 핵심 키워드만 입력해 보시겠어요?"}

    # 결과 구성
    top_results = results[:3] # 가장 유사한 3개만 보여줌
    response_text = f"🎯 입력하신 내용과 가장 유사한 기출문제를 {len(top_results)}개 찾았습니다!\n\n"
    
    for i, (score, res) in enumerate(top_results):
        response_text += f"✅ [유형 {i+1}] {res['과목']} ({res['기출연도']})\n"
        response_text += f"📝 문제: {res['문제내용_및_보기'][:100]}...\n"
        response_text += f"💡 분석 Tip: {res['해설_및_Tip']}\n"
        response_text += f"📍 정답: {res['정답']}번\n\n"

    return {"answer": response_text}