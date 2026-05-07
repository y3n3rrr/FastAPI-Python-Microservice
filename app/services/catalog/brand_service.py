from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.entities.catalog.brand import Brand
from app.repositories.catalog.brand_repository import BrandRepository
from app.schemas.catalog.brand import BrandCreate, BrandUpdate
from app.services.catalog.base import CatalogServiceBase


class BrandService(CatalogServiceBase):
    def __init__(self, repository: BrandRepository, db: Session) -> None:
        super().__init__(db)
        self.repository = repository

    def list_brands(self) -> list[Brand]:
        return self.repository.list()

    def get_brand(self, brand_id: int) -> Brand:
        brand = self.repository.get(brand_id)
        if brand is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found.")
        return brand

    def create_brand(self, payload: BrandCreate) -> Brand:
        brand = Brand(**payload.model_dump())
        self.repository.add(brand)
        return self._commit_and_refresh(
            entity=brand,
            conflict_detail="The database rejected the new brand record.",
        )

    def update_brand(self, brand_id: int, payload: BrandUpdate) -> Brand:
        brand = self.get_brand(brand_id)
        data = payload.model_dump(exclude_unset=True)
        self._set_updated_at(brand)

        for field_name, field_value in data.items():
            setattr(brand, field_name, field_value)

        return self._commit_and_refresh(
            entity=brand,
            conflict_detail="The database rejected the brand update.",
        )

    def delete_brand(self, brand_id: int) -> None:
        brand = self.get_brand(brand_id)
        self.repository.delete(brand)
        self.db.commit()
