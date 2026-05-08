from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.entities.catalog.product_variant import ProductVariant
from app.repositories.catalog.product_variant_repository import ProductVariantRepository
from app.schemas.catalog.product_variant import ProductVariantCreate, ProductVariantUpdate
from app.services.catalog.base import CatalogServiceBase


class ProductVariantService(CatalogServiceBase):
    def __init__(self, repository: ProductVariantRepository, db: Session) -> None:
        super().__init__(db)
        self.repository = repository

    def list_product_variants(self) -> list[ProductVariant]:
        return self.repository.list()

    def get_product_variant(self, variant_id: int) -> ProductVariant:
        variant = self.repository.get(variant_id)
        if variant is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product variant not found.")
        return variant

    def create_product_variant(self, payload: ProductVariantCreate) -> ProductVariant:
        variant = ProductVariant(**payload.model_dump())
        self.repository.add(variant)
        return self._commit_and_refresh(
            entity=variant,
            conflict_detail="The database rejected the new product variant record.",
        )

    def update_product_variant(self, variant_id: int, payload: ProductVariantUpdate) -> ProductVariant:
        variant = self.get_product_variant(variant_id)
        data = payload.model_dump(exclude_unset=True)
        self._set_updated_at(variant)

        for field_name, field_value in data.items():
            setattr(variant, field_name, field_value)

        return self._commit_and_refresh(
            entity=variant,
            conflict_detail="The database rejected the product variant update.",
        )

    def delete_product_variant(self, variant_id: int) -> None:
        variant = self.get_product_variant(variant_id)
        self.repository.delete(variant)
        self.db.commit()
