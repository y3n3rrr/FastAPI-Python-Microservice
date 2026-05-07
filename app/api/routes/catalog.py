from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.entities.catalog.brand import Brand
from app.entities.catalog.category import Category
from app.entities.catalog.inventory import Inventory
from app.entities.catalog.product import Product
from app.entities.catalog.product_image import ProductImage
from app.entities.catalog.product_variant import ProductVariant
from app.repositories.catalog.brand_repository import BrandRepository
from app.repositories.catalog.category_repository import CategoryRepository
from app.repositories.catalog.inventory_repository import InventoryRepository
from app.repositories.catalog.product_image_repository import ProductImageRepository
from app.repositories.catalog.product_repository import ProductRepository
from app.repositories.catalog.product_variant_repository import ProductVariantRepository
from app.schemas.catalog import (
    BrandCreate,
    BrandRead,
    BrandUpdate,
    CategoryCreate,
    CategoryRead,
    CategoryUpdate,
    InventoryCreate,
    InventoryRead,
    InventoryUpdate,
    ProductCreate,
    ProductImageCreate,
    ProductImageRead,
    ProductImageUpdate,
    ProductRead,
    ProductUpdate,
    ProductVariantCreate,
    ProductVariantRead,
    ProductVariantUpdate,
)
from app.services.catalog.brand_service import BrandService
from app.services.catalog.category_service import CategoryService
from app.services.catalog.inventory_service import InventoryService
from app.services.catalog.product_image_service import ProductImageService
from app.services.catalog.product_service import ProductService
from app.services.catalog.product_variant_service import ProductVariantService


router = APIRouter(prefix="/catalog", tags=["catalog"])


def get_brand_service(db: Session = Depends(get_db_session)) -> BrandService:
    return BrandService(repository=BrandRepository(db), db=db)


def get_category_service(db: Session = Depends(get_db_session)) -> CategoryService:
    return CategoryService(repository=CategoryRepository(db), db=db)


def get_product_service(db: Session = Depends(get_db_session)) -> ProductService:
    return ProductService(repository=ProductRepository(db), db=db)


def get_product_variant_service(db: Session = Depends(get_db_session)) -> ProductVariantService:
    return ProductVariantService(repository=ProductVariantRepository(db), db=db)


def get_product_image_service(db: Session = Depends(get_db_session)) -> ProductImageService:
    return ProductImageService(repository=ProductImageRepository(db), db=db)


def get_inventory_service(db: Session = Depends(get_db_session)) -> InventoryService:
    return InventoryService(repository=InventoryRepository(db), db=db)


@router.get("/brands", response_model=list[BrandRead])
def list_brands(service: BrandService = Depends(get_brand_service)) -> list[Brand]:
    return service.list_brands()


@router.get("/brands/{brand_id}", response_model=BrandRead)
def get_brand(brand_id: int, service: BrandService = Depends(get_brand_service)) -> Brand:
    return service.get_brand(brand_id)


@router.post("/brands", response_model=BrandRead, status_code=status.HTTP_201_CREATED)
def create_brand(payload: BrandCreate, service: BrandService = Depends(get_brand_service)) -> Brand:
    return service.create_brand(payload)


@router.put("/brands/{brand_id}", response_model=BrandRead)
def update_brand(
    brand_id: int,
    payload: BrandUpdate,
    service: BrandService = Depends(get_brand_service),
) -> Brand:
    return service.update_brand(brand_id, payload)


@router.delete("/brands/{brand_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_brand(brand_id: int, service: BrandService = Depends(get_brand_service)) -> Response:
    service.delete_brand(brand_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/categories", response_model=list[CategoryRead])
def list_categories(service: CategoryService = Depends(get_category_service)) -> list[Category]:
    return service.list_categories()


@router.get("/categories/{category_id}", response_model=CategoryRead)
def get_category(category_id: int, service: CategoryService = Depends(get_category_service)) -> Category:
    return service.get_category(category_id)


@router.post("/categories", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate, service: CategoryService = Depends(get_category_service)) -> Category:
    return service.create_category(payload)


@router.put("/categories/{category_id}", response_model=CategoryRead)
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    service: CategoryService = Depends(get_category_service),
) -> Category:
    return service.update_category(category_id, payload)


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, service: CategoryService = Depends(get_category_service)) -> Response:
    service.delete_category(category_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/products", response_model=list[ProductRead])
def list_products(service: ProductService = Depends(get_product_service)) -> list[Product]:
    return service.list_products()


@router.get("/products/{product_id}", response_model=ProductRead)
def get_product(product_id: int, service: ProductService = Depends(get_product_service)) -> Product:
    return service.get_product(product_id)


@router.post("/products", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, service: ProductService = Depends(get_product_service)) -> Product:
    return service.create_product(payload)


@router.put("/products/{product_id}", response_model=ProductRead)
def update_product(
    product_id: int,
    payload: ProductUpdate,
    service: ProductService = Depends(get_product_service),
) -> Product:
    return service.update_product(product_id, payload)


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, service: ProductService = Depends(get_product_service)) -> Response:
    service.delete_product(product_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/variants", response_model=list[ProductVariantRead])
def list_product_variants(service: ProductVariantService = Depends(get_product_variant_service)) -> list[ProductVariant]:
    return service.list_product_variants()


@router.get("/variants/{variant_id}", response_model=ProductVariantRead)
def get_product_variant(variant_id: int, service: ProductVariantService = Depends(get_product_variant_service)) -> ProductVariant:
    return service.get_product_variant(variant_id)


@router.post("/variants", response_model=ProductVariantRead, status_code=status.HTTP_201_CREATED)
def create_product_variant(
    payload: ProductVariantCreate,
    service: ProductVariantService = Depends(get_product_variant_service),
) -> ProductVariant:
    return service.create_product_variant(payload)


@router.put("/variants/{variant_id}", response_model=ProductVariantRead)
def update_product_variant(
    variant_id: int,
    payload: ProductVariantUpdate,
    service: ProductVariantService = Depends(get_product_variant_service),
) -> ProductVariant:
    return service.update_product_variant(variant_id, payload)


@router.delete("/variants/{variant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product_variant(variant_id: int, service: ProductVariantService = Depends(get_product_variant_service)) -> Response:
    service.delete_product_variant(variant_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/images", response_model=list[ProductImageRead])
def list_product_images(service: ProductImageService = Depends(get_product_image_service)) -> list[ProductImage]:
    return service.list_product_images()


@router.get("/images/{image_id}", response_model=ProductImageRead)
def get_product_image(image_id: int, service: ProductImageService = Depends(get_product_image_service)) -> ProductImage:
    return service.get_product_image(image_id)


@router.post("/images", response_model=ProductImageRead, status_code=status.HTTP_201_CREATED)
def create_product_image(payload: ProductImageCreate, service: ProductImageService = Depends(get_product_image_service)) -> ProductImage:
    return service.create_product_image(payload)


@router.put("/images/{image_id}", response_model=ProductImageRead)
def update_product_image(
    image_id: int,
    payload: ProductImageUpdate,
    service: ProductImageService = Depends(get_product_image_service),
) -> ProductImage:
    return service.update_product_image(image_id, payload)


@router.delete("/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product_image(image_id: int, service: ProductImageService = Depends(get_product_image_service)) -> Response:
    service.delete_product_image(image_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/inventory", response_model=list[InventoryRead])
def list_inventory(service: InventoryService = Depends(get_inventory_service)) -> list[Inventory]:
    return service.list_inventory()


@router.get("/inventory/{inventory_id}", response_model=InventoryRead)
def get_inventory(inventory_id: int, service: InventoryService = Depends(get_inventory_service)) -> Inventory:
    return service.get_inventory(inventory_id)


@router.post("/inventory", response_model=InventoryRead, status_code=status.HTTP_201_CREATED)
def create_inventory(payload: InventoryCreate, service: InventoryService = Depends(get_inventory_service)) -> Inventory:
    return service.create_inventory(payload)


@router.put("/inventory/{inventory_id}", response_model=InventoryRead)
def update_inventory(
    inventory_id: int,
    payload: InventoryUpdate,
    service: InventoryService = Depends(get_inventory_service),
) -> Inventory:
    return service.update_inventory(inventory_id, payload)


@router.delete("/inventory/{inventory_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_inventory(inventory_id: int, service: InventoryService = Depends(get_inventory_service)) -> Response:
    service.delete_inventory(inventory_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
