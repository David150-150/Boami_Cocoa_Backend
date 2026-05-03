import cloudinary
import cloudinary.uploader
from fastapi import UploadFile
from app.settings import settings

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET
)

async def upload_image(file: UploadFile, folder: str = "boa_mi_cocoa/users") -> str:
    contents = await file.read()
    result = cloudinary.uploader.upload(
        contents,
        folder=folder,
        resource_type="image"
    )
    return result.get("secure_url")

def upload_bytes_to_cloudinary(contents: bytes, folder: str = "boa_mi_cocoa", resource_type: str = "image") -> str:
    result = cloudinary.uploader.upload(
        contents,
        folder=folder,
        resource_type=resource_type
    )
    return result.get("secure_url")
