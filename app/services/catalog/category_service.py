from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.entities.catalog.category import Category
from app.repositories.catalog.category_repository import CategoryRepository
from app.schemas.catalog.category import CategoryCreate, CategoryUpdate
from app.services.catalog.base import CatalogServiceBase


class CategoryService(CatalogServiceBase):
    def __init__(self, repository: CategoryRepository, db: Session) -> None:
        super().__init__(db)
        self.repository = repository

    def list_categories(self) -> list[Category]:
        return self.repository.list()

    def get_category(self, category_id: int) -> Category:
        category = self.repository.get(category_id)
        if category is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found.")
        return category

    def create_category(self, payload: CategoryCreate) -> Category:
        category = Category(**payload.model_dump())
        self.repository.add(category)
        return self._commit_and_refresh(
            entity=category,
            conflict_detail="The database rejected the new category record.",
        )

    def update_category(self, category_id: int, payload: CategoryUpdate) -> Category:
        category = self.get_category(category_id)
        data = payload.model_dump(exclude_unset=True)
        self._set_updated_at(category)

        for field_name, field_value in data.items():
            setattr(category, field_name, field_value)

        return self._commit_and_refresh(
            entity=category,
            conflict_detail="The database rejected the category update.",
        )

    def delete_category(self, category_id: int) -> None:
        category = self.get_category(category_id)
        self.repository.delete(category)
        self.db.commit()
