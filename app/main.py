from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from app.routes.auth import router as auth_router
from app.routes.team import router as teams_router
from app.routes.project import router as projects_router
from app.routes.task import router as tasks_router
from app.routes.comments import router as comments_router
from app.routes.attachments import router as attachments_router
from app.routes.users import router as users_router


app = FastAPI(
    title="Syncflow",
    version="1.0.0",
    swagger_ui_oauth2_redirect_url="/oauth2-redirect",
)


app.include_router(auth_router)

app.include_router(teams_router)
app.include_router(projects_router)
app.include_router(tasks_router)
app.include_router(comments_router)
app.include_router(attachments_router)
app.include_router(users_router)


@app.get("/")
def root():
    return {"message": "hello"}





