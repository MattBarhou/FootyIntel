from fastapi import APIRouter

from app.api.routes import chat, compare, health, predict, rag, teams

api_router = APIRouter(prefix="/api")

api_router.include_router(health.router)
api_router.include_router(teams.router)
api_router.include_router(predict.router)
api_router.include_router(compare.router)
api_router.include_router(chat.router)
api_router.include_router(rag.router)
