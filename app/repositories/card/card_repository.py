import builtins

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.entities.card.card import Card


class CardRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> builtins.list[Card]:
        return list(self.db.scalars(select(Card).order_by(Card.id)))

    def get(self, card_id: int) -> Card | None:
        return self.db.get(Card, card_id)

    def list_by_user(self, user_id: int) -> builtins.list[Card]:
        return list(self.db.scalars(select(Card).where(Card.user_id == user_id).order_by(Card.id)))

    def add(self, card: Card) -> Card:
        self.db.add(card)
        return card

    def delete(self, card: Card) -> None:
        self.db.delete(card)
