from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db_session
from app.entities.user import User

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db_session),
) -> User:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized",
    )

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise unauthorized

    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise unauthorized

    subject = payload.get("sub")
    try:
        user_id = int(subject)
    except (TypeError, ValueError):
        raise unauthorized

    user = db.get(User, user_id)
    if user is None:
        raise unauthorized

    request.state.user_id = user.id

    return user
