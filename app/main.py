from fastapi import FastAPI

from app.api.routes.meeting import router as meeting_router
from app.api.routes.user import router as auth_router

app = FastAPI(title="AI Meeting Assistant")

app.include_router(meeting_router, prefix="/meetings", tags=["Meetings"])
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
