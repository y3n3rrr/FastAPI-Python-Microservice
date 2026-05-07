import builtins

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.entities.catalog.category import Category


class CategoryRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> builtins.list[Category]:
        return list(self.db.scalars(select(Category).order_by(Category.id)))

    def get(self, category_id: int) -> Category | None:
        return self.db.get(Category, category_id)

    def get_by_slug(self, slug: str) -> Category | None:
        return self.db.scalar(select(Category).where(Category.slug == slug))

    def list_children(self, parent_id: int) -> builtins.list[Category]:
        return list(self.db.scalars(select(Category).where(Category.parent_id == parent_id).order_by(Category.id)))

    def add(self, category: Category) -> Category:
        self.db.add(category)
        return category

    def delete(self, category: Category) -> None:
        self.db.delete(category)
