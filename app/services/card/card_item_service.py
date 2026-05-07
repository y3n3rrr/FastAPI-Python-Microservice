from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.entities.card.card_item import CardItem
from app.repositories.card.card_item_repository import CardItemRepository
from app.schemas.card.card_item import CardItemCreate, CardItemUpdate
from app.services.card.base import CardServiceBase


class CardItemService(CardServiceBase):
    def __init__(self, repository: CardItemRepository, db: Session) -> None:
        super().__init__(db)
        self.repository = repository

    def list_card_items(self) -> list[CardItem]:
        return self.repository.list()

    def list_items_by_card(self, card_id: int) -> list[CardItem]:
        return self.repository.list_by_card(card_id)

    def get_card_item(self, card_item_id: int) -> CardItem:
        card_item = self.repository.get(card_item_id)
        if card_item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card item not found.")
        return card_item

    def create_card_item(self, payload: CardItemCreate) -> CardItem:
        card_item = CardItem(**payload.model_dump())
        self.repository.add(card_item)
        return self._commit_and_refresh(
            entity=card_item,
            conflict_detail="The database rejected the new card item record.",
        )

    def update_card_item(self, card_item_id: int, payload: CardItemUpdate) -> CardItem:
        card_item = self.get_card_item(card_item_id)
        data = payload.model_dump(exclude_unset=True)
        self._set_updated_at(card_item)

        for field_name, field_value in data.items():
            setattr(card_item, field_name, field_value)

        return self._commit_and_refresh(
            entity=card_item,
            conflict_detail="The database rejected the card item update.",
        )

    def delete_card_item(self, card_item_id: int) -> None:
        card_item = self.get_card_item(card_item_id)
        self.repository.delete(card_item)
        self.db.commit()
