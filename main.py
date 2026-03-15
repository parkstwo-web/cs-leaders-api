from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json

app = FastAPI()

# 웹사이트(Vercel) 접속 허용 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB 불러오기
try:
    with open("CS_Leaders_기출문제_DB.json", "r", encoding="utf-8") as f:
        question_db = json.load(f)
except FileNotFoundError:
    question_db = []

class UserRequest(BaseModel):
    user_query: str

@app.post("/ask_ai")
async def get_answer(request: UserRequest):
    query = request.user_query
    relevant_data = ""
    
    for item in question_db:
        if query in item.get("문제내용_및_보기", "") or query in item.get("해설_및_Tip", ""):
            relevant_data += f"[기출연도: {item['기출연도']}]\n문제: {item['문제내용_및_보기']}\n해설 Tip: {item['해설_및_Tip']}\n"
            break

    if not relevant_data:
        return {"answer": "해당 키워드와 관련된 기출문제를 찾지 못했습니다."}

    # 현재는 AI 연결 전이므로 찾은 원본 해설을 바로 보여줍니다.
    return {"answer": f"(기출문제 DB 검색 결과)\n{relevant_data}"}