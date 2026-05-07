from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.entities.catalog.product import Product
from app.repositories.catalog.product_repository import ProductRepository
from app.schemas.catalog.product import ProductCreate, ProductUpdate
from app.services.catalog.base import CatalogServiceBase


class ProductService(CatalogServiceBase):
    def __init__(self, repository: ProductRepository, db: Session) -> None:
        super().__init__(db)
        self.repository = repository

    def list_products(self) -> list[Product]:
        return self.repository.list()

    def get_product(self, product_id: int) -> Product:
        product = self.repository.get(product_id)
        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")
        return product

    def create_product(self, payload: ProductCreate) -> Product:
        product = Product(**payload.model_dump())
        self.repository.add(product)
        return self._commit_and_refresh(
            entity=product,
            conflict_detail="The database rejected the new product record.",
        )

    def update_product(self, product_id: int, payload: ProductUpdate) -> Product:
        product = self.get_product(product_id)
        data = payload.model_dump(exclude_unset=True)
        self._set_updated_at(product)

        for field_name, field_value in data.items():
            setattr(product, field_name, field_value)

        return self._commit_and_refresh(
            entity=product,
            conflict_detail="The database rejected the product update.",
        )

    def delete_product(self, product_id: int) -> None:
        product = self.get_product(product_id)
        self.repository.delete(product)
        self.db.commit()
