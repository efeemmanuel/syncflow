from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.auth import router as auth_router
from app.routes.team import router as teams_router
from app.routes.project import router as projects_router
from app.routes.task import router as tasks_router
from app.routes.comments import router as comments_router
from app.routes.attachments import router as attachments_router
from app.routes.users import router as users_router
from app.routes.channel import router as channels_router  

app = FastAPI(title="Syncflow", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(teams_router, prefix="/api/v1")
app.include_router(projects_router, prefix="/api/v1")
app.include_router(tasks_router, prefix="/api/v1")
app.include_router(comments_router, prefix="/api/v1")
app.include_router(attachments_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(channels_router, prefix="/api/v1")  # ADD THIS