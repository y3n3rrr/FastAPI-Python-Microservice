from sqlalchemy import select
from sqlalchemy.orm import Session

from app.entities.catalog.product_image import ProductImage


class ProductImageRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> list[ProductImage]:
        return list(self.db.scalars(select(ProductImage).order_by(ProductImage.id)))

    def get(self, image_id: int) -> ProductImage | None:
        return self.db.get(ProductImage, image_id)

    def list_by_product(self, product_id: int) -> list[ProductImage]:
        stmt = select(ProductImage).where(ProductImage.product_id == product_id).order_by(ProductImage.sort_order, ProductImage.id)
        return list(self.db.scalars(stmt))

    def add(self, image: ProductImage) -> ProductImage:
        self.db.add(image)
        return image

    def delete(self, image: ProductImage) -> None:
        self.db.delete(image)
