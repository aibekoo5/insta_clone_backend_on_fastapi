from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from app.api import (
    auth,
    post,
    engagement,
    follow,
    media,
    notification,
    search,
    admin_user, 
    profile
)
from app.config import settings

app = FastAPI(title="Insta clone")

app.mount("/static", StaticFiles(directory="static"), name="static")


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(post.router)
app.include_router(engagement.router)
app.include_router(follow.router)
app.include_router(media.router)
app.include_router(notification.router)
app.include_router(search.router)
app.include_router(admin_user.router)


@app.get("/")
def read_root():
    return {"message": "Instagram Clone API"}