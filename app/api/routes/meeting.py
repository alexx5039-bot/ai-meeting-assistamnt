from fastapi import APIRouter, Depends, status, UploadFile, File

from app.db.dependencies import get_meeting_service, get_current_user
from app.models import User
from app.schemas.meeting import MeetingResponse, MeetingCreate, MeetingDetailResponse, ProcessingResponse
from app.services.meeting import MeetingService
from app.worker.tasks import process_meeting_task
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
    response_model=MeetingDetailResponse,
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

@router.post("/{meeting_id}/audio",
             response_model=MeetingResponse,
             status_code=status.HTTP_200_OK
             )
async def upload_audio(
        meeting_id: int,
        file: UploadFile = File(...),
        current_user: User = Depends(get_current_user),
        service: MeetingService = Depends(get_meeting_service)
):
    return await service.upload_audio(
        meeting_id=meeting_id,
        user_id=current_user.id,
        file=file
    )

@router.post("/{meeting_id}/process",
             response_model=ProcessingResponse,
             status_code=status.HTTP_202_ACCEPTED
             )
async def process_meeting(
        meeting_id: int,
        current_user: User = Depends(get_current_user),

):
    process_meeting_task.delay(
        meeting_id=meeting_id,
        user_id=current_user.id,
    )
    return {
        "meeting_id": meeting_id,
        "status": "processing"
    }
