import phonenumbers
from pydantic import BaseModel, validator


class UserBase(BaseModel):
    email: str
    username: str
    name: str
    phone_number: str
    address: str

    @validator("phone_number")
    def validate_phone_number(cls, phone_number):
        try:
            parsed_number = phonenumbers.parse(phone_number, None)
            if not phonenumbers.is_valid_number(parsed_number):
                raise ValueError("Invalid phone number")
        except phonenumbers.phonenumberutil.NumberParseException:
            raise ValueError("Invalid phone number")
        return phone_number


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    name: str
    phone_number: str
    address: str


class User(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True
