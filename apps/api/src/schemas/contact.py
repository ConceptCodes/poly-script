from fastapi import Form
from pydantic import BaseModel, EmailStr, Field


class ContactRequest(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr
    message: str = Field(..., min_length=1, max_length=4000)
    company: str | None = None

    @classmethod
    def as_form(
        cls,
        name: str = Form(...),
        email: EmailStr = Form(...),
        message: str = Form(...),
        company: str | None = Form(None),
    ) -> "ContactRequest":
        return cls(name=name, email=email, message=message, company=company)


class ContactResponse(BaseModel):
    status: str
