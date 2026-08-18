from fastapi import APIRouter, Depends, status

from app.db.dependencies import get_meeting_service, get_current_user
from app.models import User
from app.schemas.meeting import MeetingResponse, MeetingCreate
from app.services.meeting import MeetingService

router = APIRouter()


@router.post("",
             response_model=MeetingResponse,
             status_code=status.HTTP_201_CREATED
             )
async def create_meeting(
        data: MeetingCreate,
        current_user: User = Depends(get_current_user),
        service: MeetingService = Depends(get_meeting_service)
):
    return await service.create_meeting(
        data=data,
        user_id=current_user.id
    )

@router.get(
    "/{meeting_id}",
    response_model=MeetingResponse,
    status_code=status.HTTP_200_OK
)
async def get_meeting(
        meeting_id: int,
        current_user: User = Depends(get_current_user),
        service: MeetingService = Depends(get_meeting_service)
):
    return await service.get_meeting(meeting_id=meeting_id, user_id=current_user.id)


@router.get(
    "",
    response_model=list[MeetingResponse],
    status_code=status.HTTP_200_OK
)
async def get_meetings(
        current_user: User = Depends(get_current_user),
        service: MeetingService = Depends(get_meeting_service)
):
    return await service.get_user_meetings(current_user.id)