import os, json, logging, asyncio
from typing import List, Dict
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from pydantic import BaseModel, Field

try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

proxy = os.getenv("HTTP_PROXY")
if proxy:
    os.environ["HTTP_PROXY"] = proxy
    os.environ["HTTPS_PROXY"] = proxy

API_KEY = os.getenv("GEMINI_API_KEY", "")
if API_KEY:
    genai.configure(api_key=API_KEY)

class EvaluationResult(BaseModel):
    identified_breed: str = Field(description="识别出的品种")
    cat_title: str = Field(description="趣味称号，如：横店在逃小公举")
    total_score: int = Field(description="颜值总分 (0-100)")
    star_potential: str = Field(description="潜力等级：萌星/巨星/顶流")
    personality: str = Field(description="性格测算描述")
    detailed_analysis: Dict[str, str] = Field(description="分项亮点：head, body, charisma")
    inner_monologue: str = Field(description="猫咪内心独白")
    expert_advice: str = Field(description="经纪人出道建议")

app = FastAPI(title="猫咪颜值大赏", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

BREEDS = ["自动识别", "布偶猫", "英国短毛猫", "美国短毛猫", "其他"]

SYSTEM_INSTRUCTION = """你是一位眼光独辣、幽默风趣的“猫界金牌经纪人”。你的任务是发掘每一只猫咪的“星味”。
语言风格：幽默、高情商、以夸奖为主，善于发现萌点。严禁使用“集美”、“小仙女”等词汇。
输出要求：
1. cat_title：起一个爆款称号。
2. personality：通过表情分析性格。
3. inner_monologue：猫的视角吐槽或感慨。
4. expert_advice：给主人的建议。"""

@app.get("/")
def root(): return {"message": "猫咪颜值大赏 API"}

@app.post("/api/evaluate")
async def evaluate(file: UploadFile = File(...), breed: str = Form(...)):
    if breed not in BREEDS: raise HTTPException(status_code=400, detail="请选择品种")
    content = await file.read()
    if not API_KEY: raise HTTPException(status_code=500, detail="API Key未配置")
    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            generation_config={"response_mime_type": "application/json", "response_schema": EvaluationResult},
            system_instruction=SYSTEM_INSTRUCTION
        )
        response = await model.generate_content_async([f"品种：{breed}。请发掘它的出道潜力。", {"mime_type": file.content_type, "data": content}])
        return json.loads(response.text)
    except Exception as e:
        log.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
