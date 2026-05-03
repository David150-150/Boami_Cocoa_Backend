from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

#=========================================================#
#                   HISTORY ITEM BASE SCHEMA              #
#=========================================================#
class HistoryItem(BaseModel):
    history_id: Optional[int] = None
    scan_id: int
    disease_name: str
    urgency_level: str
    image_preview_url: str
    created_at: datetime
    status_color: Optional[str] = None

#=========================================================#
#                   HISTORY ITEM OUT SCHEMA               #
#=========================================================#
class HistoryResponse(BaseModel):
    total_scans: int
    scans: List[HistoryItem]

    model_config = ConfigDict(from_attributes=True)

