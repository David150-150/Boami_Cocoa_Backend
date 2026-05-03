from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.history import HistoryItem, HistoryResponse
from app.crud.history import add_history, get_history_by_user, delete_history
from app.db import get_db
from app.schemas.response import APIResponse
from app.auth.auth_bearer import get_current_user
from app.models.history import History
from app.models.scan import Scan
from app.models.disease import Disease

router = APIRouter()

COLOR_MAP = {
    "High": "red",
    "Medium": "orange",
    "Low": "green"
}

# ==============================================================
# ADD A SCAN TO USER HISTORY
# ==============================================================
@router.post("/add/{scan_id}", response_model=APIResponse[HistoryItem])
def add_to_history(
    scan_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        user_id = current_user.user_id

        new_history = add_history(db, user_id, scan_id)

        disease_name = "Unknown"
        urgency_level = "Low"

        if new_history.scan and new_history.scan.disease:
            disease_name = new_history.scan.disease.name
            urgency_level = new_history.scan.urgency_level or "Low"

        history_item = HistoryItem(
            history_id=new_history.history_id,
            scan_id=new_history.scan_id,
            disease_name=disease_name,
            urgency_level=urgency_level,
            image_preview_url=new_history.scan.image_url if new_history.scan else None,
            created_at=new_history.viewed_at,
            status_color=COLOR_MAP.get(urgency_level, "green")
        )

        return APIResponse(
            success=True,
            message="History recorded successfully",
            data=history_item
        )

    except HTTPException:
        raise
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"History creation failed: {str(e)}",
            data=None
        )


# ==============================================================
# GET CURRENT USER FULL SCAN HISTORY
# ==============================================================
@router.get("/me", response_model=APIResponse[HistoryResponse])
def get_my_history(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        user_id = current_user.user_id

        history_entries = get_history_by_user(db, user_id, limit)

        scans = []

        for h in history_entries:
            disease_name = "Unknown"
            urgency_level = "Low"

            if h.scan:
                urgency_level = h.scan.urgency_level or "Low"
                if h.scan.disease:
                    disease_name = h.scan.disease.name

            scans.append(HistoryItem(
                history_id=h.history_id,
                scan_id=h.scan_id,
                disease_name=disease_name,
                urgency_level=urgency_level,
                image_preview_url=h.scan.image_url if h.scan else None,
                created_at=h.viewed_at,
                status_color=COLOR_MAP.get(urgency_level, "green")
            ))

        return APIResponse(
            success=True,
            message=f"Found {len(scans)} history records",
            data=HistoryResponse(
                total_scans=len(scans),
                scans=scans
            )
        )

    except HTTPException:
        raise
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"Failed to fetch history: {str(e)}",
            data=None
        )


# ==============================================================
# DELETE HISTORY ENTRY
# ==============================================================
@router.delete("/delete/{history_id}", response_model=APIResponse)
def remove_history(
    history_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        delete_history(db, history_id)

        return APIResponse(
            success=True,
            message="History deleted successfully",
            data=None
        )

    except HTTPException:
        raise
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"History deletion failed: {str(e)}",
            data=None
        )