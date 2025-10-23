"""
音频样本上传 API 路由
路径：backend/src/api/routes/voice.py
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from services.voice_synthesis import VoiceSynthesisService
from api.dependencies import get_voice_synthesis_service

router = APIRouter()

@router.post("/voice/upload")
async def upload_voice_sample(
    audio: UploadFile = File(...),
    voice_service: VoiceSynthesisService = Depends(get_voice_synthesis_service)
):
    """
    上传用户音频样本，用于定制专属音色
    参数：audio - 用户上传的音频文件
    返回：音色配置结果（如 voice_id、状态等）
    """
    if audio.content_type not in ["audio/wav", "audio/mpeg"]:
        raise HTTPException(status_code=400, detail="仅支持WAV/MP3音频上传")
    result = await voice_service.create_voice_profile(audio)
    return {"success": True, "data": result}
