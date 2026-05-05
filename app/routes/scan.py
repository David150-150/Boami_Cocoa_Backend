# # from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
# # from sqlalchemy.orm import Session
# # from typing import List, Optional
# # from pydantic import ValidationError
# # from app.crud.scan import (
# #     create_scan, get_all_scans, get_scan_by_id,
# #     get_scans_by_user, update_scan, delete_scan
# # )
# # from app.schemas.scan import ScanCreate, ScanUpdate, ScanOut
# # from app.db import get_db
# # from app.schemas.response import APIResponse
# # from app.auth.auth_bearer import get_current_user
# # from app.ai.image_predictor import ImagePredictor
# # from app.models.disease import Disease
# # from app.services.cloudinary_service import upload_bytes_to_cloudinary

# # #from app.utils.cloudinary_upload import upload_to_cloudinary   # ← NEW
# # # ← removed: import os, import uuid (no longer needed)
# # import logging

# # logger = logging.getLogger(__name__)
# # predictor = ImagePredictor()
# # router = APIRouter()


# # #==============================================================#
# # #       PREDICT DISEASE FROM IMAGE AND SAVE SCAN               #
# # #==============================================================#
# # @router.post("/predict", response_model=APIResponse[dict])
# # async def predict_disease(
# #     file: UploadFile = File(...),
# #     latitude: Optional[float] = None,
# #     longitude: Optional[float] = None,
# #     db: Session = Depends(get_db),
# #     current_user=Depends(get_current_user)
# # ):
# #     try:
# #         if not file.content_type.startswith('image/'):
# #             raise HTTPException(400, "File must be an image")

# #         image_bytes = await file.read()

# #         result = predictor.predict(image_bytes)
# #         predicted_name = str(result.get("predicted_disease", "Unknown"))
# #         confidence = float(result.get("confidence", 0.0))

# #         # ── Upload image to Cloudinary ──────────────────────
# #         # Replaces the old os.makedirs / uuid / open(...wb) block
# #         #image_url = upload_to_cloudinary(image_bytes, folder="scans/image", resource_type="image")
# #         image_url = upload_bytes_to_cloudinary(image_bytes, folder="boa_mi_cocoa/scans/image")
# #         # ────────────────────────────────────────────────────

# #         disease = db.query(Disease).filter(
# #             Disease.name.ilike(f"%{predicted_name.replace(' ', '_')}%")
# #         ).first()

# #         urgency = "High" if confidence >= 0.8 else "Medium" if confidence >= 0.5 else "Low"

# #         scan_data = ScanCreate(
# #             user_id=int(current_user._id),
# #             image_url=image_url,           # ← Cloudinary URL
# #             disease_id=int(disease.disease_id) if disease else None,
# #             custom_label=predicted_name,
# #             confidence_score=confidence,
# #             urgency_level=urgency,
# #             latitude=latitude,
# #             longitude=longitude
# #         )
# #         saved_scan = create_scan(db, scan_data)

# #         return APIResponse(success=True, message="Success", data={
# #             "scan_id": saved_scan.scan_id,
# #             "image_url": image_url,        # ← Cloudinary URL in response
# #             "predicted_disease": predicted_name,
# #             "confidence": confidence,
# #             "urgency_level": urgency,
# #             "disease_found_in_db": disease is not None
# #         })

# #     except ValidationError as e:
# #         raise HTTPException(422, f"Validation error: {e}")
# #     except HTTPException:
# #         raise
# #     except Exception as e:
# #         logger.error(f"Predict error: {e}")
# #         raise HTTPException(500, f"Prediction failed: {str(e)}")


# # #==============================================================#
# # #                  GET ALL SCANS BY USER                       #
# # #==============================================================#
# # @router.get("/user/{user_id}", response_model=List[ScanOut])
# # def read_scans_by_user(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
# #     try:
# #         return get_scans_by_user(db, user_id, skip=skip, limit=limit)
# #     except HTTPException:
# #         raise
# #     except Exception as e:
# #         raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Failed to fetch user scans: {str(e)}")


# # #==============================================================#
# # #                      CREATE SCAN                             #
# # #==============================================================#
# # @router.post("/", response_model=APIResponse[ScanOut])
# # def add_scan(scan: ScanCreate, db: Session = Depends(get_db)):
# #     try:
# #         new_scan = create_scan(db, scan)
# #         return APIResponse(success=True, message="Scan created successfully", data=new_scan)
# #     except Exception as e:
# #         return APIResponse(success=False, message=f"Scan creation failed: {str(e)}", data=None)


# # #==============================================================#
# # #                      GET ALL SCANS                           #
# # #==============================================================#
# # @router.get("/", response_model=List[ScanOut])
# # def read_scans(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
# #     try:
# #         return get_all_scans(db, skip=skip, limit=limit)
# #     except Exception as e:
# #         raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Failed to fetch scans: {str(e)}")


# # #==============================================================#
# # #                 GET SINGLE SCAN BY ID                        #
# # #==============================================================#
# # @router.get("/{scan_id}", response_model=ScanOut)
# # def read_scan(scan_id: int, db: Session = Depends(get_db)):
# #     try:
# #         return get_scan_by_id(db, scan_id)
# #     except HTTPException:
# #         raise
# #     except Exception as e:
# #         raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Failed to fetch scan: {str(e)}")


# # #==============================================================#
# # #                         UPDATE A SCAN                        #
# # #==============================================================#
# # @router.put("/{scan_id}", response_model=APIResponse[ScanOut])
# # def modify_scan(scan_id: int, scan_update: ScanUpdate, db: Session = Depends(get_db)):
# #     try:
# #         updated_scan = update_scan(db, scan_id, scan_update)
# #         return APIResponse(success=True, message="Scan updated successfully", data=updated_scan)
# #     except Exception as e:
# #         return APIResponse(success=False, message=f"Scan update failed: {str(e)}", data=None)


# # #==============================================================#
# # #                         DELETE SCAN                          #
# # #==============================================================#
# # @router.delete("/{scan_id}", response_model=APIResponse[dict])
# # def remove_scan(scan_id: int, db: Session = Depends(get_db)):
# #     try:
# #         delete_scan(db, scan_id)
# #         return APIResponse(success=True, message="Scan deleted successfully", data=None)
# #     except Exception as e:
# #         return APIResponse(success=False, message=f"Scan deletion failed: {str(e)}", data=None)



# # #python app/ai/train.py  python app/ai/train.py


# # from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
# # from sqlalchemy.orm import Session
# # from typing import Optional, List
# # from pydantic import ValidationError
# # import base64
# # import io
# # import logging
# # from PIL import Image

# # from app.crud.scan import (
# #     create_scan, get_all_scans, get_scan_by_id,
# #     get_scans_by_user, update_scan, delete_scan
# # )
# # from app.schemas.scan import ScanCreate, ScanUpdate, ScanOut
# # from app.db import get_db
# # from app.schemas.response import APIResponse
# # from app.auth.auth_bearer import get_current_user
# # from app.ai.image_predictor import ImagePredictor
# # from app.models.disease import Disease
# # from app.services.cloudinary_service import upload_bytes_to_cloudinary

# # logger = logging.getLogger(__name__)
# # router = APIRouter()
# # predictor = ImagePredictor()

# # # ==============================================================
# # # 🔥 PREDICT + GRAD-CAM + SAVE SCAN
# # # ==============================================================
# # @router.post("/predict", response_model=APIResponse[dict])
# # async def predict_disease(
# #     file: UploadFile = File(...),
# #     latitude: Optional[float] = None,
# #     longitude: Optional[float] = None,
# #     db: Session = Depends(get_db),
# #     current_user=Depends(get_current_user)
# # ):
# #     try:
# #         # Validate image
# #         if not file.content_type.startswith("image/"):
# #             raise HTTPException(status_code=400, detail="File must be an image")

# #         image_bytes = await file.read()

# #         # =========================
# #         # 1. AI PREDICTION
# #         # =========================
# #         result = predictor.predict(image_bytes)
# #         predicted_name = str(result.get("disease") or result.get("predicted_disease") or "Unknown")
# #         confidence = float(result.get("confidence", 0.0))

# #         # =========================
# #         # 2. CLOUDINARY UPLOAD
# #         # =========================
# #         image_url = upload_bytes_to_cloudinary(
# #             image_bytes,
# #             folder="boa_mi_cocoa/scans/image"
# #         )

# #         # =========================
# #         # 3. FIND DISEASE IN DB
# #         # =========================
# #         disease = db.query(Disease).filter(
# #             Disease.name.ilike(f"%{predicted_name}%")
# #         ).first()

# #         urgency = (
# #             "High" if confidence >= 0.8
# #             else "Medium" if confidence >= 0.5
# #             else "Low"
# #         )

# #         # =========================
# #         # 4. SAVE SCAN
# #         # =========================
# #         scan_data = ScanCreate(
# #             user_id=int(current_user._id),
# #             image_url=image_url,
# #             disease_id=int(disease.disease_id) if disease else None,
# #             custom_label=predicted_name,
# #             confidence_score=confidence,
# #             urgency_level=urgency,
# #             latitude=latitude,
# #             longitude=longitude
# #         )

# #         saved_scan = create_scan(db, scan_data)

# #         # =========================
# #         # 5. 🔥 GRAD-CAM GENERATION
# #         # =========================
# #         heatmap = predictor.generate_gradcam(image_bytes)
# #         overlay = predictor.overlay_heatmap(image_bytes, heatmap)

# #         overlay_img = Image.fromarray(overlay)
# #         buffer = io.BytesIO()
# #         overlay_img.save(buffer, format="JPEG")

# #         gradcam_base64 = base64.b64encode(buffer.getvalue()).decode()

# #         # =========================
# #         # 6. RESPONSE
# #         # =========================
# #         return APIResponse(
# #             success=True,
# #             message="Prediction successful",
# #             data={
# #                 "scan_id": saved_scan.scan_id,
# #                 "image_url": image_url,
# #                 "predicted_disease": predicted_name,
# #                 "confidence": confidence,
# #                 "urgency_level": urgency,
# #                 "disease_found_in_db": disease is not None,
# #                 "gradcam_image": gradcam_base64
# #             }
# #         )

# #     except ValidationError as e:
# #         raise HTTPException(status_code=422, detail=str(e))

# #     except Exception as e:
# #         logger.error(f"Prediction error: {e}")
# #         raise HTTPException(status_code=500, detail=str(e))


# # # ==============================================================
# # # 📊 GET SCANS BY USER
# # # ==============================================================
# # @router.get("/user/{user_id}", response_model=List[ScanOut])
# # def read_scans_by_user(
# #     user_id: int,
# #     skip: int = 0,
# #     limit: int = 100,
# #     db: Session = Depends(get_db)
# # ):
# #     return get_scans_by_user(db, user_id, skip=skip, limit=limit)


# # # ==============================================================
# # # ➕ CREATE SCAN (manual)
# # # ==============================================================
# # @router.post("/", response_model=APIResponse[ScanOut])
# # def add_scan(scan: ScanCreate, db: Session = Depends(get_db)):
# #     new_scan = create_scan(db, scan)
# #     return APIResponse(success=True, message="Created", data=new_scan)


# # # ==============================================================
# # # 📄 GET ALL SCANS
# # # ==============================================================
# # @router.get("/", response_model=List[ScanOut])
# # def read_scans(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
# #     return get_all_scans(db, skip=skip, limit=limit)


# # # ==============================================================
# # # 🔍 GET SINGLE SCAN
# # # ==============================================================
# # @router.get("/{scan_id}", response_model=ScanOut)
# # def read_scan(scan_id: int, db: Session = Depends(get_db)):
# #     return get_scan_by_id(db, scan_id)


# # # ==============================================================
# # # ✏️ UPDATE SCAN
# # # ==============================================================
# # @router.put("/{scan_id}", response_model=APIResponse[ScanOut])
# # def modify_scan(scan_id: int, scan_update: ScanUpdate, db: Session = Depends(get_db)):
# #     updated = update_scan(db, scan_id, scan_update)
# #     return APIResponse(success=True, message="Updated", data=updated)


# # # ==============================================================
# # # ❌ DELETE SCAN
# # # ==============================================================
# # @router.delete("/{scan_id}", response_model=APIResponse[dict])
# # def remove_scan(scan_id: int, db: Session = Depends(get_db)):
# #     delete_scan(db, scan_id)
# #     return APIResponse(success=True, message="Deleted", data=None)










# # app/routes/scan.py

# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from typing import List
# import logging

# from app.crud.scan import (
#     create_scan, get_all_scans, get_scan_by_id,
#     get_scans_by_user, update_scan, delete_scan
# )
# from app.schemas.scan import ScanCreate, ScanUpdate, ScanOut
# from app.db import get_db
# from app.schemas.response import APIResponse
# from app.auth.auth_bearer import get_current_user

# logger = logging.getLogger(__name__)
# router = APIRouter()


# # ================================================================
# # GET ALL SCANS
# # ================================================================
# @router.get("/", response_model=List[ScanOut])
# def read_scans(
#     skip: int = 0,
#     limit: int = 100,
#     db: Session = Depends(get_db)
# ):
#     return get_all_scans(db, skip=skip, limit=limit)


# # ================================================================
# # GET SCANS BY USER
# # ================================================================
# @router.get("/user/{user_id}", response_model=List[ScanOut])
# def read_scans_by_user(
#     user_id: int,
#     skip: int = 0,
#     limit: int = 100,
#     db: Session = Depends(get_db)
# ):
#     return get_scans_by_user(db, user_id, skip=skip, limit=limit)


# # ================================================================
# # GET MY SCANS  (current logged-in user)
# # ================================================================
# @router.get("/me", response_model=APIResponse)
# def read_my_scans(
#     skip: int = 0,
#     limit: int = 100,
#     db: Session = Depends(get_db),
#     current_user=Depends(get_current_user)
# ):
#     scans = get_scans_by_user(db, int(current_user.user_id), skip=skip, limit=limit)
#     return APIResponse(
#         success=True,
#         message=f"{len(scans)} scans found",
#         data=scans
#     )


# # ================================================================
# # GET SINGLE SCAN
# # ================================================================
# @router.get("/{scan_id}", response_model=APIResponse)
# def read_scan(
#     scan_id: int,
#     db: Session = Depends(get_db),
#     current_user=Depends(get_current_user)
# ):
#     scan = get_scan_by_id(db, scan_id)
#     if not scan:
#         raise HTTPException(status_code=404, detail="Scan not found")
#     return APIResponse(success=True, message="Scan found", data=scan)


# # ================================================================
# # CREATE SCAN (manual — without AI)
# # ================================================================
# @router.post("/", response_model=APIResponse)
# def add_scan(
#     scan: ScanCreate,
#     db: Session = Depends(get_db),
#     current_user=Depends(get_current_user)
# ):
#     new_scan = create_scan(db, scan)
#     return APIResponse(success=True, message="Scan created", data=new_scan)


# # ================================================================
# # UPDATE SCAN
# # ================================================================
# @router.put("/{scan_id}", response_model=APIResponse)
# def modify_scan(
#     scan_id: int,
#     scan_update: ScanUpdate,
#     db: Session = Depends(get_db),
#     current_user=Depends(get_current_user)
# ):
#     updated = update_scan(db, scan_id, scan_update)
#     if not updated:
#         raise HTTPException(status_code=404, detail="Scan not found")
#     return APIResponse(success=True, message="Scan updated", data=updated)


# # ================================================================
# # DELETE SCAN
# # ================================================================
# @router.delete("/{scan_id}", response_model=APIResponse)
# def remove_scan(
#     scan_id: int,
#     db: Session = Depends(get_db),
#     current_user=Depends(get_current_user)
# ):
#     delete_scan(db, scan_id)
#     return APIResponse(success=True, message="Scan deleted", data=None)






from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import logging

from app.crud.scan import (
    create_scan, get_all_scans, get_scan_by_id,
    get_scans_by_user, update_scan, delete_scan
)
from app.schemas.scan import ScanCreate, ScanUpdate, ScanOut
from app.db import get_db
from app.schemas.response import APIResponse
from app.auth.auth_bearer import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

# ================================================================
# GET ALL SCANS
# ================================================================
@router.get("/", response_model=List[ScanOut])
def read_scans(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_all_scans(db, skip=skip, limit=limit)

# ================================================================
# GET SCANS BY USER
# ================================================================
@router.get("/user/{user_id}", response_model=List[ScanOut])
def read_scans_by_user(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_scans_by_user(db, user_id, skip=skip, limit=limit)

# ================================================================
# GET MY SCANS (current user)
# ================================================================
@router.get("/me", response_model=APIResponse)
def read_my_scans(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    scans = get_scans_by_user(db, int(current_user.user_id), skip=skip, limit=limit)
    return APIResponse(success=True, message=f"{len(scans)} scans found", data=scans)

# ================================================================
# GET SINGLE SCAN - FIXED ✅
# ================================================================
@router.get("/{scan_id}", response_model=APIResponse)
def read_scan(scan_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    scan = get_scan_by_id(db, scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return APIResponse(success=True, message="Scan found", data=scan)

# ================================================================
# CREATE SCAN
# ================================================================
@router.post("/", response_model=APIResponse)
def add_scan(scan: ScanCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    new_scan = create_scan(db, scan)
    return APIResponse(success=True, message="Scan created", data=new_scan)

# ================================================================
# UPDATE SCAN
# ================================================================
@router.put("/{scan_id}", response_model=APIResponse)
def modify_scan(scan_id: int, scan_update: ScanUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    updated = update_scan(db, scan_id, scan_update)
    return APIResponse(success=True, message="Scan updated", data=updated)

# ================================================================
# DELETE SCAN
# ================================================================
@router.delete("/{scan_id}", response_model=APIResponse)
def remove_scan(scan_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    delete_scan(db, scan_id)
    return APIResponse(success=True, message="Scan deleted", data=None)