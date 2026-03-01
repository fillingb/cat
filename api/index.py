"""
猫咪品相评估 API - FastAPI + Gemini 2.5 Flash
"""
import os
import json
import logging
import asyncio
from typing import List, Dict

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from google.generativeai.types import GenerateContentResponse
from pydantic import BaseModel, Field

# 加载环境变量（如果存在 .env 文件）
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# 配置代理与 API Key
os.environ.setdefault("HTTP_PROXY", os.getenv("HTTP_PROXY", "http://127.0.0.1:7897"))
os.environ.setdefault("HTTPS_PROXY", os.getenv("HTTPS_PROXY", "http://127.0.0.1:7897"))
API_KEY = os.getenv("GEMINI_API_KEY", "")

if API_KEY:
    genai.configure(api_key=API_KEY)

# --- 数据模型定义 (用于 Structured Outputs) ---
class DetailedAnalysis(BaseModel):
    head: str = Field(description="头部与五官缺陷/优点描述")
    body: str = Field(description="身体骨量与比例描述")
    coat: str = Field(description="被毛质地、花纹、颜色描述")

class EvaluationResult(BaseModel):
    identified_breed: str = Field(description="识别出的品种")
    total_score: int = Field(description="综合评分 (0-100)")
    grade: str = Field(description="等级：赛级/繁育级/宠物级")
    detailed_analysis: DetailedAnalysis
    pros: List[str] = Field(description="核心优点 (1-3条)")
    cons: List[str] = Field(description="核心缺陷 (1-3条)")
    price_estimate: str = Field(description="市场价格预估区间")
    expert_advice: str = Field(description="具体的专家进阶建议")

app = FastAPI(title="猫咪品相评估", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BREEDS = ["自动识别", "布偶猫", "英国短毛猫", "美国短毛猫", "其他"]

SYSTEM_INSTRUCTION = """你是一位深耕猫咪品种研究 20 年的专业繁育顾问与 CFA 全品种资深审查员。你的职责是基于极其严苛的赛级标准，为用户提供客观、精准且具备审美洞察力的品相评估报告。

[核心人设]
- 风格：优雅、客观、理性、专业。
- 禁忌：严禁使用“集美”、“小仙女”、“家人们”等网络俗语。
- 目标：不仅指出猫咪是否漂亮，更要从解剖学结构、骨量、被毛质感等深度维度分析其市场价值与潜在风险。

[评分维度]
1. 赛级 (90-100): 结构完美，具备极佳的品种典型性，展现出卓越的展示状态。
2. 繁育级 (80-89): 品种特征明确，但在细微比例（如耳位、眼色深浅、尾部长度）上有可见偏差。
3. 宠物级 (<80): 绝大多数家养猫属于此类。存在明显的品相瑕疵（如花纹不对称、骨量不足、侧颜曲线平淡）。

[避坑指南要求]
请仔细观察照片中的细节，如是否有泪痕（暗示鼻泪管问题）、耳道是否干净、眼神是否暗淡、毛发是否干枯。给出真正能帮用户在购买时避雷的建议。"""

@app.get("/")
def root():
    return {"message": "猫咪品相评估 API", "status": "running"}

@app.post("/api/evaluate")
async def evaluate(
    file: UploadFile = File(...),
    breed: str = Form(...),
):
    if breed not in BREEDS:
        raise HTTPException(status_code=400, detail="请选择正确的品种")
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="请上传有效的图片文件")

    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="图片超过 10MB")

    if not API_KEY or "YOUR_GEMINI_API_KEY" in API_KEY:
        log.error("未配置有效的 GEMINI_API_KEY")
        raise HTTPException(status_code=500, detail="服务器未配置 API Key，请检查环境变量。")

    try:
        # 使用 Structured Outputs (JSON Schema)
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            generation_config={
                "response_mime_type": "application/json",
                "response_schema": EvaluationResult,
            },
            system_instruction=SYSTEM_INSTRUCTION
        )

        image_part = {"mime_type": file.content_type, "data": content}
        prompt = f"请评估该猫咪的品相。用户声称品种为：{breed}。如果图片显示不是该品种，请在识别结果中修正。"

        log.info("正在发送请求至 Gemini...")
        response = await model.generate_content_async([prompt, image_part])
        
        if not response.text:
            raise ValueError("Gemini 未返回任何内容")
            
        result_data = json.loads(response.text)
        
        # 简单校验
        if result_data.get("total_score", 0) >= 90:
            result_data["grade"] = "赛级"
        elif result_data.get("total_score", 0) >= 80:
            result_data["grade"] = "繁育级"
        else:
            result_data["grade"] = "宠物级"

        log.info("评估成功: Score=%d", result_data.get("total_score"))
        return result_data

    except Exception as e:
        log.error("评估流程出错: %s", str(e))
        raise HTTPException(status_code=500, detail=f"评估失败: {str(e)}")
