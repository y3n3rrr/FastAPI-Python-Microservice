from sqlalchemy import select
from sqlalchemy.orm import Session

from app.entities.catalog.brand import Brand


class BrandRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> list[Brand]:
        return list(self.db.scalars(select(Brand).order_by(Brand.id)))

    def get(self, brand_id: int) -> Brand | None:
        return self.db.get(Brand, brand_id)

    def get_by_slug(self, slug: str) -> Brand | None:
        return self.db.scalar(select(Brand).where(Brand.slug == slug))

    def add(self, brand: Brand) -> Brand:
        self.db.add(brand)
        return brand

    def delete(self, brand: Brand) -> None:
        self.db.delete(brand)
