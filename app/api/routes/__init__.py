from app.api.routes.auth import router as auth_router
from app.api.routes.cart import router as cart_router
from app.api.routes.catalog import router as catalog_router
from app.api.routes.health import router as health_router
from app.api.routes.orders import router as orders_router
from app.api.routes.users import router as users_router

__all__ = ["auth_router", "cart_router", "catalog_router", "health_router", "orders_router", "users_router"]
