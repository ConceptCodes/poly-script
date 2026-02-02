import logging
from fastapi import APIRouter, Depends

from src.schemas.contact import ContactRequest, ContactResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["contact"])


@router.post("/v1/contact", response_model=ContactResponse)
async def submit_contact(
    request: ContactRequest = Depends(ContactRequest.as_form),
) -> ContactResponse:
    logger.info(
        "Contact submission received",
        extra={"contact_email": request.email, "contact_name": request.name},
    )
    return ContactResponse(status="received")
