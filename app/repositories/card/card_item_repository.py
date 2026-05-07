import builtins

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.entities.card.card_item import CardItem


class CardItemRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> builtins.list[CardItem]:
        return list(self.db.scalars(select(CardItem).order_by(CardItem.id)))

    def get(self, card_item_id: int) -> CardItem | None:
        return self.db.get(CardItem, card_item_id)

    def list_by_card(self, card_id: int) -> builtins.list[CardItem]:
        return list(self.db.scalars(select(CardItem).where(CardItem.card_id == card_id).order_by(CardItem.id)))

    def get_by_card_and_variant(self, card_id: int, product_variant_id: int) -> CardItem | None:
        stmt = select(CardItem).where(
            CardItem.card_id == card_id,
            CardItem.product_variant_id == product_variant_id,
        )
        return self.db.scalar(stmt)

    def add(self, card_item: CardItem) -> CardItem:
        self.db.add(card_item)
        return card_item

    def delete(self, card_item: CardItem) -> None:
        self.db.delete(card_item)
