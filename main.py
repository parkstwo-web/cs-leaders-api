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
async def get_similar_questions(request: UserRequest):
    query = request.user_query
    # 입력된 텍스트에서 불필요한 공백과 특수문자 제거 (정확도 향상)
    clean_query = re.sub(r'\s+', '', query)
    
    results = []
    
    for item in question_db:
        # 문제 내용과 보기에서 공백 제거 후 비교
        db_content = re.sub(r'\s+', '', item.get("문제내용_및_보기", ""))
        
        # 1. 문장이 완벽히 일치하거나
        # 2. 입력된 긴 문장 안에 DB의 핵심 내용이 포함되어 있거나
        # 3. 반대로 DB 내용 안에 입력된 키워드가 있을 경우
        if clean_query in db_content or db_content in clean_query:
            results.append(item)
            
    if not results:
        # 만약 통째로 일치하는 게 없다면 핵심 키워드 검색 시도
        return {"answer": "죄송합니다. 정확히 일치하는 문제를 찾지 못했습니다. 문제의 핵심 키워드(예: '서비스 매트릭스', '가시선') 위주로 다시 검색해 보세요."}

    # 동일 유형 결과 구성
    response_text = f"🎯 총 {len(results)}개의 동일/유사 유형 문제를 찾았습니다!\n\n"
    for i, res in enumerate(results[:5]): # 너무 많을 수 있으니 상위 5개만 출력
        response_text += f"--- [유사유형 {i+1}] ---\n"
        response_text += f"▶ 출제: {res['과목']} ({res['기출연도']})\n"
        response_text += f"▶ 문제: {res['문제내용_및_보기'][:100]}...\n" # 앞부분만 노출
        response_text += f"▶ 정답: {res['정답']}\n"
        response_text += f"▶ 분석 Tip: {res['해설_및_Tip']}\n\n"

    return {"answer": response_text}