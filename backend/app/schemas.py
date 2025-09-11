from pydantic import BaseModel, Field, computed_field
from typing import Optional
from datetime import datetime

# ---- Demographics ----
class DemographicsIn(BaseModel):
    program_use_only: bool = False
    ASURite: str = Field(..., min_length=1)
    Gender: str
    Age: str
    Race_Ethnicity: str
    Race_Ethnicity_Specify: str = ""
    Major: str
    Major_Category: str
    Major_Category_Specify: str = ""
    Language_Background: str
    Native_Language: str = ""
    Years_Studied_English: str = ""
    Years_in_US: str = ""

class DemographicsOut(BaseModel):
    asurite: str
    saved: bool

# ---- Writing Session ----
class StartSessionIn(BaseModel):
    asurite: str

class StartSessionOut(BaseModel):
    session_id: str
    started_at: datetime

class EssaySubmitIn(BaseModel):
    session_id: str
    essay_text: str

class EssaySubmitOut(BaseModel):
    session_id: str
    submitted_at: datetime
    duration_seconds: int
    word_count: int
    char_count: int

# ---- Common ----
class MessageOut(BaseModel):
    message: str
