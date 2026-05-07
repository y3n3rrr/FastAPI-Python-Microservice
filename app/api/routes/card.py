from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.entities.card.card import Card
from app.entities.card.card_item import CardItem
from app.repositories.card.card_item_repository import CardItemRepository
from app.repositories.card.card_repository import CardRepository
from app.schemas.card import (
    CardCreate,
    CardItemCreate,
    CardItemRead,
    CardItemUpdate,
    CardRead,
    CardUpdate,
)
from app.services.card.card_item_service import CardItemService
from app.services.card.card_service import CardService


router = APIRouter(prefix="/cards", tags=["cards"])


def get_card_service(db: Session = Depends(get_db_session)) -> CardService:
    return CardService(repository=CardRepository(db), db=db)


def get_card_item_service(db: Session = Depends(get_db_session)) -> CardItemService:
    return CardItemService(repository=CardItemRepository(db), db=db)


@router.get("", response_model=list[CardRead])
def list_cards(service: CardService = Depends(get_card_service)) -> list[Card]:
    return service.list_cards()


@router.get("/users/{user_id}", response_model=list[CardRead])
def list_user_cards(user_id: int, service: CardService = Depends(get_card_service)) -> list[Card]:
    return service.list_user_cards(user_id)


@router.get("/items", response_model=list[CardItemRead])
def list_card_items(service: CardItemService = Depends(get_card_item_service)) -> list[CardItem]:
    return service.list_card_items()


@router.get("/{card_id}/items", response_model=list[CardItemRead])
def list_items_by_card(card_id: int, service: CardItemService = Depends(get_card_item_service)) -> list[CardItem]:
    return service.list_items_by_card(card_id)


@router.get("/items/{card_item_id}", response_model=CardItemRead)
def get_card_item(card_item_id: int, service: CardItemService = Depends(get_card_item_service)) -> CardItem:
    return service.get_card_item(card_item_id)


@router.post("/items", response_model=CardItemRead, status_code=status.HTTP_201_CREATED)
def create_card_item(payload: CardItemCreate, service: CardItemService = Depends(get_card_item_service)) -> CardItem:
    return service.create_card_item(payload)


@router.put("/items/{card_item_id}", response_model=CardItemRead)
def update_card_item(
    card_item_id: int,
    payload: CardItemUpdate,
    service: CardItemService = Depends(get_card_item_service),
) -> CardItem:
    return service.update_card_item(card_item_id, payload)


@router.delete("/items/{card_item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_card_item(card_item_id: int, service: CardItemService = Depends(get_card_item_service)) -> Response:
    service.delete_card_item(card_item_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{card_id}", response_model=CardRead)
def get_card(card_id: int, service: CardService = Depends(get_card_service)) -> Card:
    return service.get_card(card_id)


@router.post("", response_model=CardRead, status_code=status.HTTP_201_CREATED)
def create_card(payload: CardCreate, service: CardService = Depends(get_card_service)) -> Card:
    return service.create_card(payload)


@router.put("/{card_id}", response_model=CardRead)
def update_card(card_id: int, payload: CardUpdate, service: CardService = Depends(get_card_service)) -> Card:
    return service.update_card(card_id, payload)


@router.delete("/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_card(card_id: int, service: CardService = Depends(get_card_service)) -> Response:
    service.delete_card(card_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
