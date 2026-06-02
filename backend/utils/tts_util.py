"""
阿里云语音合成(TTS)封装
将文本转为语音，支持多种音色
"""
import httpx
import base64
import logging
from typing import Optional
from backend.config import settings

logger = logging.getLogger("tts")


async def text_to_speech(
    text: str,
    voice: str = "zhichu",
    format: str = "mp3",
    sample_rate: int = 16000,
) -> Optional[bytes]:
    """
    文本转语音
    :param text: 要合成的文本 (最长300字符)
    :param voice: 音色名称
    :param format: 音频格式 mp3/pcm/wav
    :param sample_rate: 采样率
    :return: 音频二进制数据
    """
    if len(text) > 300:
        text = text[:300]
        logger.warning("TTS文本超过300字符，已截断")

    headers = {
        "Authorization": f"Bearer {settings.ALIYUN_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": settings.ALIYUN_TTS_MODEL,
        "input": {"text": text},
        "parameters": {
            "voice": voice,
            "format": format,
            "sample_rate": sample_rate,
        },
    }

    logger.info("合成请求 text=%d字符 voice=%s", len(text), voice)

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{settings.ALIYUN_BASE_URL}/services/audio/text-to-speech/synthesis",
            headers=headers,
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()

        audio_b64 = data.get("output", {}).get("audio", "")
        if audio_b64:
            audio_data = base64.b64decode(audio_b64)
            logger.info("合成成功 audio=%d字节", len(audio_data))
            return audio_data
        else:
            logger.error("合成失败: %s", data)
            return None


async def text_to_speech_url(
    text: str,
    voice: str = "zhichu",
) -> Optional[str]:
    """
    文本转语音，返回临时URL
    用于前端直接播放
    """
    audio_data = await text_to_speech(text, voice)
    if not audio_data:
        return None

    import uuid
    from pathlib import Path

    upload_dir = Path(settings.UPLOAD_DIR) / "tts"
    upload_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid.uuid4().hex}.mp3"
    filepath = upload_dir / filename
    filepath.write_bytes(audio_data)

    return f"/uploads/tts/{filename}"
