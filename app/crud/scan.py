# from sqlalchemy.orm import Session
# from fastapi import HTTPException, status
# from app.models.scan import Scan
# from app.schemas.scan import ScanCreate, ScanUpdate
# from app.crud.expert import get_smart_expert
# from app.models.consult import Consultation
# from app.models.notification import Notification


# from app.crud.expert import get_smart_expert
# from app.crud.consult import create_consultation
# from app.crud.notification import create_notification
# from app.schemas.consult import ConsultationCreate




# def create_scan(db: Session, scan: ScanCreate):
#     # Create Scan
#     db_scan = Scan(
#         user_id=scan.user_id,
#         disease_id=scan.disease_id,
#         image_url=scan.image_url,
#         custom_label=scan.custom_label,
#         confidence_score=scan.confidence_score,
#         urgency_level=scan.urgency_level,
#         latitude=scan.latitude,
#         longitude=scan.longitude
#     )

#     db.add(db_scan)
#     db.commit()
#     db.refresh(db_scan)

#     # Auto Assign Smart Expert
#     if scan.latitude and scan.longitude:
#         expert = get_smart_expert(db, scan.latitude, scan.longitude)
#         if expert:
#             # Auto Create Consultation
#             consultation_data = ConsultationCreate(
#                 user_id=scan.user_id,
#                 scan_id=db_scan.scan_id,
#                 expert_id=expert.expert_id,
#                 subject="AI Detected Disease",
#                 description="Automatic consultation created after AI scan",
#                 priority=scan.urgency_level if scan.urgency_level else "Medium"
#             )
#             create_consultation(db, scan.user_id, consultation_data)

#             # Update Expert Workload
#             expert.current_workload += 1
#             db.commit()

#             # Async Notifications
#             import asyncio
#             asyncio.create_task(
#                 create_notification(
#                     db=db,
#                     user_id=expert.expert_id,
#                     role="expert",
#                     title="New Consultation Assigned",
#                     content=f"You have a new consultation for scan #{db_scan.scan_id}"
#                 )
#             )
#             asyncio.create_task(
#                 create_notification(
#                     db=db,
#                     user_id=scan.user_id,
#                     role="user",
#                     title="Expert Assigned",
#                     content="An expert has been assigned to your scan"
#                 )
#             )

#     return db_scan



# # -----------------------------
# # Get all scans (optional pagination)
# # -----------------------------
# def get_all_scans(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(Scan).offset(skip).limit(limit).all()

# # -----------------------------
# # Get scan by ID
# # -----------------------------
# def get_scan_by_id(db: Session, scan_id: int):
#     scan = db.query(Scan).filter(Scan.scan_id == scan_id).first()
#     if not scan:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found")
#     return scan

# # -----------------------------
# # Get scans by user
# # -----------------------------
# def get_scans_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
#     return db.query(Scan).filter(Scan.user_id == user_id).offset(skip).limit(limit).all()

# # -----------------------------
# # Update a scan
# # -----------------------------
# # def update_scan(db: Session, scan_id: int, scan_update: ScanUpdate):
# #     scan = db.query(Scan).filter(Scan.scan_id == scan_id).first()
# #     if not scan:
# #         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found")
    
# #     update_data = scan_update.dict(exclude_unset=True)
# #     for key, value in update_data.items():
# #         setattr(scan, key, value)
    
# #     db.commit()
# #     db.refresh(scan)
# #     return scan
# def update_scan(db: Session, scan_id: int, scan_update):
#     scan = db.query(Scan).filter(Scan.scan_id == scan_id).first()

#     if not scan:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Scan not found"
#         )

#     # Handle Pydantic model OR dict
#     if hasattr(scan_update, "dict"):
#         update_data = scan_update.dict(exclude_unset=True)
#     else:
#         update_data = scan_update

#     for key, value in update_data.items():
#         setattr(scan, key, value)

#     db.commit()
#     db.refresh(scan)

#     return scan

# # -----------------------------
# # Delete a scan
# # -----------------------------
# def delete_scan(db: Session, scan_id: int):
#     scan = db.query(Scan).filter(Scan.scan_id == scan_id).first()
#     if not scan:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found")
    
#     db.delete(scan)
#     db.commit()
#     return {"message": "Scan deleted successfully"}





from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.scan import Scan
from app.schemas.scan import ScanCreate, ScanUpdate
from app.crud.expert import get_smart_expert
from app.models.consult import Consultation
from app.models.notification import Notification
from app.crud.consult import create_consultation
from app.crud.notification import create_notification
from app.schemas.consult import ConsultationCreate
import asyncio

def create_scan(db: Session, scan: ScanCreate):
    # Create Scan
    db_scan = Scan(
        user_id=scan.user_id,
        disease_id=scan.disease_id,
        image_url=scan.image_url,
        custom_label=scan.custom_label,
        confidence_score=scan.confidence_score,
        urgency_level=scan.urgency_level,
        latitude=scan.latitude,
        longitude=scan.longitude
    )

    db.add(db_scan)
    db.commit()
    db.refresh(db_scan)

    # Auto Assign Smart Expert
    if scan.latitude and scan.longitude:
        expert = get_smart_expert(db, scan.latitude, scan.longitude)
        if expert:
            # Auto Create Consultation
            consultation_data = ConsultationCreate(
                user_id=scan.user_id,
                scan_id=db_scan.scan_id,
                expert_id=expert.expert_id,
                subject="AI Detected Disease",
                description="Automatic consultation created after AI scan",
                priority=scan.urgency_level if scan.urgency_level else "Medium"
            )
            create_consultation(db, scan.user_id, consultation_data)

            # Update Expert Workload
            expert.current_workload += 1
            db.commit()

            # Async Notifications
            asyncio.create_task(
                create_notification(
                    db=db,
                    user_id=expert.expert_id,
                    role="expert",
                    title="New Consultation Assigned",
                    content=f"You have a new consultation for scan #{db_scan.scan_id}"
                )
            )
            asyncio.create_task(
                create_notification(
                    db=db,
                    user_id=scan.user_id,
                    role="user",
                    title="Expert Assigned",
                    content="An expert has been assigned to your scan"
                )
            )

    return db_scan

# -----------------------------
# Get all scans (pagination)
# -----------------------------
def get_all_scans(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Scan).offset(skip).limit(limit).all()

# -----------------------------
# Get scan by ID - FIXED ✅
# -----------------------------
def get_scan_by_id(db: Session, scan_id: int):
    return db.query(Scan).filter(Scan.scan_id == scan_id).first()  # Just return scan or None

# -----------------------------
# Get scans by user
# -----------------------------
def get_scans_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(Scan).filter(Scan.user_id == user_id).offset(skip).limit(limit).all()

# -----------------------------
# Update a scan
# -----------------------------
def update_scan(db: Session, scan_id: int, scan_update: ScanUpdate):
    scan = db.query(Scan).filter(Scan.scan_id == scan_id).first()
    
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found"
        )

    update_data = scan_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(scan, key, value)

    db.commit()
    db.refresh(scan)
    return scan

# -----------------------------
# Delete a scan
# -----------------------------
def delete_scan(db: Session, scan_id: int):
    scan = db.query(Scan).filter(Scan.scan_id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found")
    
    db.delete(scan)
    db.commit()
    return {"message": "Scan deleted successfully"}