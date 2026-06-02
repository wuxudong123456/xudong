"""
阿里云语音识别(ASR)封装
将语音转为文本
"""
import httpx
import base64
import logging
from typing import Optional
from backend.config import settings

logger = logging.getLogger("asr")


async def speech_to_text(
    audio_data: bytes,
    format: str = "mp3",
    sample_rate: int = 16000,
) -> Optional[str]:
    """
    语音转文本
    :param audio_data: 音频二进制数据
    :param format: 音频格式
    :param sample_rate: 采样率
    :return: 识别出的文本
    """
    audio_base64 = base64.b64encode(audio_data).decode("utf-8")

    headers = {
        "Authorization": f"Bearer {settings.ALIYUN_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": settings.ALIYUN_ASR_MODEL,
        "input": {
            "audio": audio_base64,
            "format": format,
            "sample_rate": sample_rate,
        },
    }

    logger.info("识别请求 audio=%d字节", len(audio_data))

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{settings.ALIYUN_BASE_URL}/services/audio/asr/transcriptions",
            headers=headers,
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()

        text = data.get("output", {}).get("text", "")
        logger.info("识别结果: %s", text[:50] if text else "")
        return text if text else None
