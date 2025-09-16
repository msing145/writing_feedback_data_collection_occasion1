from pydantic import BaseModel, Field
from datetime import datetime

# ---- Demographics ----
class DemographicsIn(BaseModel):
    program_use_only: bool = False

    asurite: str = Field(..., alias="ASURite", min_length=1)

    gender: str = Field(..., alias="Gender")
    age: str = Field(..., alias="Age")

    race_ethnicity: str = Field(..., alias="Race_Ethnicity")
    race_ethnicity_specify: str = Field("", alias="Race_Ethnicity_Specify")

    major: str = Field("", alias="Major")
    major_category: str = Field("", alias="Major_Category")
    major_category_specify: str = Field("", alias="Major_Category_Specify")

    language_background: str = Field(..., alias="Language_Background")
    native_language: str = Field("", alias="Native_Language")
    years_studied_english: str = Field("", alias="Years_Studied_English")
    years_in_us: str = Field("", alias="Years_in_US")

    class Config:
        populate_by_name = True  # accept both alias (PascalCase) and lowercase


class DemographicsOut(BaseModel):
    asurite: str
    saved: bool


# ---- Writing Session ----
class StartSessionIn(BaseModel):
    asurite: str = Field(..., alias="ASURite")

    class Config:
        populate_by_name = True


class StartSessionOut(BaseModel):
    session_id: str
    started_at: datetime


class EssaySubmitIn(BaseModel):
    session_id: str = Field(..., alias="Session_Id")
    essay_text: str = Field(..., alias="Essay_Text")

    class Config:
        populate_by_name = True


class EssaySubmitOut(BaseModel):
    session_id: str
    submitted_at: datetime
    duration_seconds: int
    word_count: int
    char_count: int


# ---- Common ----
class MessageOut(BaseModel):
    message: str
