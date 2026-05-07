from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.entities.card.card import Card
from app.repositories.card.card_repository import CardRepository
from app.schemas.card.card import CardCreate, CardUpdate
from app.services.card.base import CardServiceBase


class CardService(CardServiceBase):
    def __init__(self, repository: CardRepository, db: Session) -> None:
        super().__init__(db)
        self.repository = repository

    def list_cards(self) -> list[Card]:
        return self.repository.list()

    def list_user_cards(self, user_id: int) -> list[Card]:
        return self.repository.list_by_user(user_id)

    def get_card(self, card_id: int) -> Card:
        card = self.repository.get(card_id)
        if card is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found.")
        return card

    def create_card(self, payload: CardCreate) -> Card:
        card = Card(**payload.model_dump())
        self.repository.add(card)
        return self._commit_and_refresh(
            entity=card,
            conflict_detail="The database rejected the new card record.",
        )

    def update_card(self, card_id: int, payload: CardUpdate) -> Card:
        card = self.get_card(card_id)
        data = payload.model_dump(exclude_unset=True)
        self._set_updated_at(card)

        for field_name, field_value in data.items():
            setattr(card, field_name, field_value)

        return self._commit_and_refresh(
            entity=card,
            conflict_detail="The database rejected the card update.",
        )

    def delete_card(self, card_id: int) -> None:
        card = self.get_card(card_id)
        self.repository.delete(card)
        self.db.commit()
