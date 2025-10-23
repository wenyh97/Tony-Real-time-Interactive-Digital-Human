"""
数字人形象定制 - 图片上传 API 路由
路径：backend/src/api/routes/appearance.py
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from services.avatar_generation import AvatarGenerationService
from api.dependencies import get_avatar_generation_service

router = APIRouter()

@router.post("/appearance/upload")
async def upload_appearance_image(
    image: UploadFile = File(...),
    avatar_service: AvatarGenerationService = Depends(get_avatar_generation_service)
):
    """
    上传用户图片并生成数字人模型
    参数：image - 用户上传的图片文件
    返回：模型生成结果（如模型ID、预览URL等）
    """
    if image.content_type not in ["image/png", "image/jpeg"]:
        raise HTTPException(status_code=400, detail="仅支持PNG/JPEG图片上传")
    result = await avatar_service.generate_avatar(image)
    return {"success": True, "data": result}
