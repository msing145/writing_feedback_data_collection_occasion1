from datetime import datetime
from pydantic import BaseModel, Field
from pydantic import ConfigDict  # pydantic v2

# ---- Demographics ----
class DemographicsIn(BaseModel):
    # Accept both old PascalCase keys and new lowercase keys
    model_config = ConfigDict(populate_by_name=True)

    program_use_only: bool = False

    asurite: str = Field(..., alias="ASURite", min_length=1)
    gender: str = Field(..., alias="Gender")
    age: str = Field(..., alias="Age")

    # Packed value: "Hispanic_Origin=Yes|No; Race=A, B, C"
    race_ethnicity: str = Field(..., alias="Race_Ethnicity")
    race_ethnicity_specify: str = Field("", alias="Race_Ethnicity_Specify")

    # Optional / legacy
    major: str = Field("", alias="Major")
    major_category: str = Field("", alias="Major_Category")
    major_category_specify: str = Field("", alias="Major_Category_Specify")

    language_background: str = Field(..., alias="Language_Background")
    native_language: str = Field("", alias="Native_Language")
    years_studied_english: str = Field("", alias="Years_Studied_English")
    years_in_us: str = Field("", alias="Years_in_US")


class DemographicsOut(BaseModel):
    asurite: str
    saved: bool


# ---- Writing Session ----
class StartSessionIn(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    asurite: str = Field(..., alias="ASURite")


class StartSessionOut(BaseModel):
    session_id: str
    started_at: datetime


class EssaySubmitIn(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    session_id: str = Field(..., alias="Session_Id")
    essay_text: str = Field(..., alias="Essay_Text")


class EssaySubmitOut(BaseModel):
    session_id: str
    submitted_at: datetime
    duration_seconds: int
    word_count: int
    char_count: int


# ---- Common ----
class MessageOut(BaseModel):
    message: str
