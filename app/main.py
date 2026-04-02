from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from app.routes.auth import router as auth_router



app = FastAPI(
    title="Syncflow",
    version="1.0.0",
    swagger_ui_oauth2_redirect_url="/oauth2-redirect",
)


app.include_router(auth_router)

@app.get("/")
def root():
    return {"message": "hello"}



