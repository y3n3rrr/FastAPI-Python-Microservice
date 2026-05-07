from fastapi import APIRouter, Depends

from app.api.dependencies.auth import get_current_user
from app.api.routes.auth import router as auth_router
from app.api.routes.card import router as card_router
from app.api.routes.catalog import router as catalog_router
from app.api.routes.health import router as health_router
from app.api.routes.orders import router as orders_router
from app.api.routes.users import router as users_router


api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(health_router, dependencies=[Depends(get_current_user)])
api_router.include_router(users_router, dependencies=[Depends(get_current_user)])
api_router.include_router(card_router, dependencies=[Depends(get_current_user)])
api_router.include_router(catalog_router, dependencies=[Depends(get_current_user)])
api_router.include_router(orders_router, dependencies=[Depends(get_current_user)])
