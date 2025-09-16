from pydantic import BaseModel, Field
from datetime import datetime

# ---- Demographics ----
class DemographicsIn(BaseModel):
    program_use_only: bool = False
    asurite: str = Field(..., min_length=1)

    gender: str
    age: str

    race_ethnicity: str
    race_ethnicity_specify: str = ""

    major: str = ""
    major_category: str = ""
    major_category_specify: str = ""

    language_background: str
    native_language: str = ""
    years_studied_english: str = ""
    years_in_us: str = ""

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
