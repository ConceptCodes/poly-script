from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from fastapi import Form


class ContactRequest(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr
    message: str = Field(..., min_length=1, max_length=4000)
    company: Optional[str] = None

    @classmethod
    def as_form(
        cls,
        name: str = Form(...),
        email: EmailStr = Form(...),
        message: str = Form(...),
        company: Optional[str] = Form(None),
    ) -> "ContactRequest":
        return cls(name=name, email=email, message=message, company=company)


class ContactResponse(BaseModel):
    status: str
