from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator


class BabyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    birth_date: date

    # Like a Rails `validate :birth_date_not_in_future`. Raising ValueError
    # turns into a 422 response with a readable error message.
    @field_validator("birth_date")
    @classmethod
    def not_in_the_future(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("birth date can't be in the future")
        return value


class BabyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    birth_date: date
