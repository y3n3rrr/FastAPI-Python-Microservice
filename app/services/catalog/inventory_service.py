from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.entities.catalog.inventory import Inventory
from app.repositories.catalog.inventory_repository import InventoryRepository
from app.schemas.catalog.inventory import InventoryCreate, InventoryUpdate
from app.services.catalog.base import CatalogServiceBase


class InventoryService(CatalogServiceBase):
    def __init__(self, repository: InventoryRepository, db: Session) -> None:
        super().__init__(db)
        self.repository = repository

    def list_inventory(self) -> list[Inventory]:
        return self.repository.list()

    def get_inventory(self, inventory_id: int) -> Inventory:
        inventory = self.repository.get(inventory_id)
        if inventory is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory record not found.")
        return inventory

    def create_inventory(self, payload: InventoryCreate) -> Inventory:
        inventory = Inventory(**payload.model_dump())
        self.repository.add(inventory)
        return self._commit_and_refresh(
            entity=inventory,
            conflict_detail="The database rejected the new inventory record.",
        )

    def update_inventory(self, inventory_id: int, payload: InventoryUpdate) -> Inventory:
        inventory = self.get_inventory(inventory_id)
        data = payload.model_dump(exclude_unset=True)
        self._set_updated_at(inventory)

        for field_name, field_value in data.items():
            setattr(inventory, field_name, field_value)

        return self._commit_and_refresh(
            entity=inventory,
            conflict_detail="The database rejected the inventory update.",
        )

    def delete_inventory(self, inventory_id: int) -> None:
        inventory = self.get_inventory(inventory_id)
        self.repository.delete(inventory)
        self.db.commit()
