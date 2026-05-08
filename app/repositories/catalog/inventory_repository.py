from sqlalchemy import select
from sqlalchemy.orm import Session

from app.entities.catalog.inventory import Inventory


class InventoryRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> list[Inventory]:
        return list(self.db.scalars(select(Inventory).order_by(Inventory.id)))

    def get(self, inventory_id: int) -> Inventory | None:
        return self.db.get(Inventory, inventory_id)

    def get_by_variant_id(self, variant_id: int) -> Inventory | None:
        return self.db.scalar(select(Inventory).where(Inventory.variant_id == variant_id))

    def add(self, inventory: Inventory) -> Inventory:
        self.db.add(inventory)
        return inventory

    def delete(self, inventory: Inventory) -> None:
        self.db.delete(inventory)
