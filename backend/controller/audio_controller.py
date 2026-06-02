"""
语音交互控制器 — 语音识别 + 语音合成
"""
import base64
import logging
from fastapi import APIRouter, Depends, UploadFile, File
from pydantic import BaseModel, Field
from backend.dependencies import get_current_user
from backend.entity.user import User

router = APIRouter(tags=["语音交互"])
logger = logging.getLogger(__name__)


class SynthesizeRequest(BaseModel):
    text: str = Field(..., max_length=300, description="要合成的文本")
    voice: str = Field("zhichu", description="音色")


@router.post("/recognize", summary="语音识别")
async def recognize_speech(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """上传音频文件 → 返回识别文本"""
    try:
        audio_bytes = await file.read()
        from backend.utils.asr_util import speech_to_text
        text = await speech_to_text(audio_bytes)
        if text:
            return {"code": 200, "data": {"text": text}, "message": "success"}
        return {"code": 500, "message": "语音识别失败：未识别到文字", "data": None}
    except Exception as e:
        logger.error("ASR failed: %s", e)
        return {"code": 500, "message": f"语音识别失败: {e}", "data": None}


@router.post("/synthesize", summary="语音合成")
async def synthesize_speech(
    req: SynthesizeRequest,
    current_user: User = Depends(get_current_user),
):
    """文本 → base64 音频"""
    try:
        from backend.utils.tts_util import text_to_speech
        audio_bytes = await text_to_speech(req.text, voice=req.voice)
        if audio_bytes:
            audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
            return {"code": 200, "data": {"audio_base64": audio_b64, "format": "mp3"},
                    "message": "success"}
        return {"code": 500, "message": "语音合成失败", "data": None}
    except Exception as e:
        logger.error("TTS failed: %s", e)
        return {"code": 500, "message": f"语音合成失败: {e}", "data": None}
