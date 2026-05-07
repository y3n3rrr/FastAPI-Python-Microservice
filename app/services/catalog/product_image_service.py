from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.entities.catalog.product_image import ProductImage
from app.repositories.catalog.product_image_repository import ProductImageRepository
from app.schemas.catalog.product_image import ProductImageCreate, ProductImageUpdate
from app.services.catalog.base import CatalogServiceBase


class ProductImageService(CatalogServiceBase):
    def __init__(self, repository: ProductImageRepository, db: Session) -> None:
        super().__init__(db)
        self.repository = repository

    def list_product_images(self) -> list[ProductImage]:
        return self.repository.list()

    def get_product_image(self, image_id: int) -> ProductImage:
        image = self.repository.get(image_id)
        if image is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product image not found.")
        return image

    def create_product_image(self, payload: ProductImageCreate) -> ProductImage:
        image = ProductImage(**payload.model_dump())
        self.repository.add(image)
        return self._commit_and_refresh(
            entity=image,
            conflict_detail="The database rejected the new product image record.",
        )

    def update_product_image(self, image_id: int, payload: ProductImageUpdate) -> ProductImage:
        image = self.get_product_image(image_id)
        data = payload.model_dump(exclude_unset=True)
        self._set_updated_at(image)

        for field_name, field_value in data.items():
            setattr(image, field_name, field_value)

        return self._commit_and_refresh(
            entity=image,
            conflict_detail="The database rejected the product image update.",
        )

    def delete_product_image(self, image_id: int) -> None:
        image = self.get_product_image(image_id)
        self.repository.delete(image)
        self.db.commit()
