from pydantic import BaseModel, EmailStr


class UserInfo(BaseModel):
    username: str
    email: EmailStr
    phone: str | None = None
