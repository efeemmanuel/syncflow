from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from app.routes.auth import router as auth_router
from app.routes.team import router as teams_router
from app.routes.project import router as projects_router



app = FastAPI(
    title="Syncflow",
    version="1.0.0",
    swagger_ui_oauth2_redirect_url="/oauth2-redirect",
)


app.include_router(auth_router)

app.include_router(teams_router)
app.include_router(projects_router)

@app.get("/")
def root():
    return {"message": "hello"}





