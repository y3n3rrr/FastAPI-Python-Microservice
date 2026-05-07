import builtins

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.entities.payment.payment_intent import PaymentIntent


class PaymentIntentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> builtins.list[PaymentIntent]:
        return list(self.db.scalars(select(PaymentIntent).order_by(PaymentIntent.id)))

    def get(self, payment_intent_id: int) -> PaymentIntent | None:
        return self.db.get(PaymentIntent, payment_intent_id)

    def add(self, payment_intent: PaymentIntent) -> PaymentIntent:
        self.db.add(payment_intent)
        return payment_intent
