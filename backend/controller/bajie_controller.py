"""
八戒功能接口控制层
提供灯谜游戏、飞花令、情绪疏导、社交僚机、角色对话等API
"""
from typing import Optional, List
from fastapi import APIRouter, Query, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from backend.dependencies import get_db, get_current_user
from backend.entity.user import User
from backend.service.bajie_service import BajieService

router = APIRouter()


# ===== 请求模型 =====
class RiddleAnswerRequest(BaseModel):
    riddle_text: str = Field(..., description="谜面")
    answer: str = Field(..., description="用户答案")
    correct_answer: str = Field("", description="正确答案（LLM灯谜需传入）")

class PoetryAnswerRequest(BaseModel):
    line: str = Field(..., description="上句")
    answer: str = Field(..., description="用户对的下句")

class ChatRequest(BaseModel):
    message: str = Field(..., description="用户消息")
    history: Optional[List[dict]] = Field(None, description="对话历史")

class EmotionalRequest(BaseModel):
    message: str = Field(..., description="倾诉内容")

class ChatLinesRequest(BaseModel):
    scenario: str = Field(..., description="场景: first_meet/flirt/apologize/care/invite/confess")
    personality: str = Field(..., description="对方性格: outgoing/shy/independent/gentle")
    extra_info: str = Field("", description="补充信息")

class LoveLetterRequest(BaseModel):
    to: str = Field("亲爱的", description="收信人")
    style: str = Field("romantic", description="风格: romantic/humorous/sincere")
    memory: str = Field("", description="关键回忆")

# ===== 飞花令请求/响应模型 =====
class FeihualingAnswerRequest(BaseModel):
    keyword: str = Field(..., description="关键字")
    answer: str = Field(..., description="用户回答的诗词句")

class FeihualingStartRequest(BaseModel):
    keyword: Optional[str] = Field(None, description="指定字，不指定则随机")

# ===== 成语接龙请求模型 =====
class ChengyuAnswerRequest(BaseModel):
    prev_last_char: str = Field(..., description="上一个成语尾字")
    answer: str = Field(..., description="用户回答的成语")
    history: List[str] = Field([], description="已用成语列表")

class ChengyuStartRequest(BaseModel):
    start_word: Optional[str] = Field(None, description="起始成语")


# ===== 灯谜接口 =====
@router.get("/riddle", summary="获取随机灯谜")
def get_riddle(
    difficulty: Optional[str] = Query(None, description="难度: 简单/中等/困难"),
    current_user: User = Depends(get_current_user),
):
    """随机返回一道灯谜（不含答案）"""
    service = BajieService()
    riddle = service.get_random_riddle(difficulty)
    return {"code": 200, "message": "哼哼～俺来出题！", "data": riddle}


@router.post("/riddle/check", summary="校验灯谜答案")
def check_riddle(
    req: RiddleAnswerRequest,
    current_user: User = Depends(get_current_user),
):
    """校验灯谜答案，返回对/错和积分变化"""
    service = BajieService()
    result = service.check_riddle_answer(req.riddle_text, req.answer)
    return {"code": 200, "message": result["message"], "data": result}


# ===== 飞花令接口 =====
@router.get("/poetry", summary="获取随机诗词上句")
def get_poetry(current_user: User = Depends(get_current_user)):
    """随机返回一句诗词上句，等待用户对下句"""
    service = BajieService()
    poetry = service.get_random_poetry()
    return {"code": 200, "message": "请对出下句！", "data": poetry}


@router.post("/poetry/check", summary="校验对诗答案")
async def check_poetry(
    req: PoetryAnswerRequest,
    current_user: User = Depends(get_current_user),
):
    """校验对诗答案，使用DeepSeek语义相似度评判"""
    service = BajieService()
    result = await service.check_poetry_answer(req.line, req.answer)
    return {"code": 200, "message": result["message"], "data": result}


# ===== 飞花令单字接龙接口 =====
@router.post("/feihualing/start", summary="开始飞花令")
def start_feihualing(
    req: FeihualingStartRequest = None,
    current_user: User = Depends(get_current_user),
):
    """开始飞花令单字接龙，指定或随机选关键字"""
    service = BajieService()
    result = service.start_feihualing(req.keyword if req else None)
    return {"code": 200, "message": f"飞花令开始！关键字：「{result['keyword']}」", "data": result}


@router.post("/feihualing/check", summary="校验飞花令")
async def check_feihualing(
    req: FeihualingAnswerRequest,
    current_user: User = Depends(get_current_user),
):
    """校验用户的飞花令回答"""
    service = BajieService()
    result = await service.check_feihualing(req.keyword, req.answer)
    return {"code": 200, "message": result["message"], "data": result}


# ===== LLM 灯谜接口 =====
@router.get("/riddle/llm", summary="获取LLM生成灯谜")
async def get_riddle_llm(
    topic: Optional[str] = Query(None, description="主题：四大名著/成语/日常物品/动物/自然现象/历史人物"),
    current_user: User = Depends(get_current_user),
):
    """使用DeepSeek生成随机灯谜（含答案，前端不显示）"""
    service = BajieService()
    riddle = await service.generate_riddle_llm(topic)
    return {"code": 200, "message": "哼哼～俺来出题！", "data": riddle}


@router.post("/riddle/check/llm", summary="校验LLM灯谜答案")
async def check_riddle_llm(
    req: RiddleAnswerRequest,
    current_user: User = Depends(get_current_user),
):
    """校验LLM生成灯谜的答案（语义匹配）"""
    service = BajieService()
    result = await service.check_riddle_llm(req.riddle_text, req.correct_answer, req.answer)
    return {"code": 200, "message": result["message"], "data": result}


# ===== 成语接龙接口 =====
@router.post("/chengyu/start", summary="开始成语接龙")
def start_chengyu(
    req: ChengyuStartRequest = None,
    current_user: User = Depends(get_current_user),
):
    """开始成语接龙游戏"""
    service = BajieService()
    result = service.start_chengyu_chain(req.start_word if req else None)
    return {"code": 200, "message": f"成语接龙开始！起始：「{result['word']}」", "data": result}


@router.post("/chengyu/check", summary="校验成语接龙")
async def check_chengyu(
    req: ChengyuAnswerRequest,
    current_user: User = Depends(get_current_user),
):
    """校验用户成语 + 八戒自动接龙回复"""
    service = BajieService()
    user_result = await service.check_chengyu(req.prev_last_char, req.answer, req.history)
    if user_result["correct"]:
        new_history = req.history + [user_result["word"]]
        bot_reply = await service.chengyu_bot_reply(user_result.get("next_char", req.answer[-1]), new_history)
        if bot_reply.get("word"):
            new_history.append(bot_reply["word"])
        return {
            "code": 200, "message": user_result["message"],
            "data": {"user": user_result, "bot": bot_reply, "history": new_history},
        }
    return {"code": 200, "message": user_result["message"], "data": {"user": user_result, "history": req.history}}


# ===== 角色对话接口 =====
@router.post("/chat", summary="八戒角色对话")
async def bajie_chat(
    req: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    """猪八戒角色扮演对话"""
    service = BajieService()
    service._user_id = current_user.id
    reply = await service.bajie_chat(req.message, req.history)
    return {"code": 200, "message": "success", "data": {"reply": reply}}


# ===== 情绪疏导接口 =====
@router.post("/emotional", summary="情绪疏导")
async def emotional_support(
    req: EmotionalRequest,
    current_user: User = Depends(get_current_user),
):
    """八戒情绪疏导（共情五步法）"""
    service = BajieService()
    reply = await service.emotional_support(req.message)
    return {"code": 200, "message": "success", "data": {"reply": reply}}


@router.get("/night-check", summary="深夜关怀检查")
def night_check(current_user: User = Depends(get_current_user)):
    """检查当前是否为深夜时段，返回关怀话术"""
    service = BajieService()
    is_night = service.is_night_time()
    greeting = service.get_night_greeting() if is_night else "白天好呀！"
    return {"code": 200, "message": "success", "data": {"is_night": is_night, "greeting": greeting}}


# ===== 社交僚机接口 =====
@router.post("/chat-lines", summary="生成聊天话术")
async def generate_chat_lines(
    req: ChatLinesRequest,
    current_user: User = Depends(get_current_user),
):
    """八戒社交僚机 - 生成聊天话术"""
    service = BajieService()
    lines = await service.generate_chat_lines(req.scenario, req.personality, req.extra_info)
    return {"code": 200, "message": "俺老猪给你支几招！", "data": {"lines": lines}}


@router.post("/love-letter", summary="代写情书")
async def write_love_letter(
    req: LoveLetterRequest,
    current_user: User = Depends(get_current_user),
):
    """八戒社交僚机 - 代写情书"""
    service = BajieService()
    letter = await service.write_love_letter(req.to, req.style, req.memory)
    return {"code": 200, "message": "情书写好啦！", "data": {"letter": letter}}
