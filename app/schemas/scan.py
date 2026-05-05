
# from pydantic import BaseModel, Field, ConfigDict
# from typing import Optional, List
# from datetime import datetime


# #=========================================================#
# #                      SCAN BASE SCHEMA                   #
# #=========================================================#

# class ScanBase(BaseModel):
#     disease_id: Optional[int] = None
#     custom_label: Optional[str] = None
#     confidence_score: Optional[float] = Field(..., ge=0, le=1)
#     latitude: Optional[float] = None
#     longitude: Optional[float] = None

# #=========================================================#
# #                      SCAN CREATE SCHEMA                 #
# #=========================================================#
# class ScanCreate(ScanBase):
#     user_id: int
#     image_url: Optional[str] = None
#     urgency_level: Optional[str] = None 
#     description: Optional[str] = None  
      


# #=========================================================#
# #                      SCAN UPDATE SCHEMA                 #
# #=========================================================#
# class ScanUpdate(BaseModel):
#     disease_id: Optional[int] = None
#     custom_label: Optional[str] = None
#     confidence_score: Optional[float] = Field(None, ge=0, le=1)
#     latitude: Optional[float] = None
#     longitude: Optional[float] = None
#     urgency_level: Optional[str] = None

# #=========================================================#
# #                      SCAN OUT SCHEMA                    #
# #=========================================================#
# class ScanOut(ScanBase):
#     scan_id: int
#     user_id: int
#     image_url:  Optional[str] = None
#     confidence_score: Optional[float] = None
#     custom_label: Optional[str] = None
#     created_at: datetime
#     urgency_level: Optional[str] = None

#     model_config = ConfigDict(from_attributes=True)





from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

#=========================================================#
#                      SCAN BASE SCHEMA                   #
#=========================================================#
class ScanBase(BaseModel):
    disease_id: Optional[int] = None
    custom_label: Optional[str] = None
    confidence_score: Optional[float] = Field(None, ge=0, le=1)  # ⭐ Fixed default
    latitude: Optional[float] = None
    longitude: Optional[float] = None

#=========================================================#
#                      SCAN CREATE SCHEMA                 #
#=========================================================#
class ScanCreate(ScanBase):
    user_id: int
    image_url: Optional[str] = None
    urgency_level: Optional[str] = None 
    description: Optional[str] = None  

#=========================================================#
#                      SCAN UPDATE SCHEMA                 #
#=========================================================#
class ScanUpdate(BaseModel):
    disease_id: Optional[int] = None
    custom_label: Optional[str] = None
    confidence_score: Optional[float] = Field(None, ge=0, le=1)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    urgency_level: Optional[str] = None

#=========================================================#
# FIXED SCAN OUT SCHEMA - MATCHES SQLALCHEMY ✅
#=========================================================#
class ScanOut(BaseModel):  # ⭐ NO INHERITANCE - explicit fields
    scan_id: int
    user_id: int
    disease_id: Optional[int] = None
    image_url: Optional[str] = None
    audio_url: Optional[str] = None
    custom_label: Optional[str] = None
    confidence_score: Optional[float] = None
    urgency_level: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True  # ⭐ CRITICAL
    )

