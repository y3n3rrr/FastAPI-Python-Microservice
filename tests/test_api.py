import os
import time
import unittest
from pathlib import Path

from sqlalchemy import create_engine


class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.database_path = Path("tests") / "test_app.db"
        if cls.database_path.exists():
            cls.database_path.unlink()
        os.environ["APP_DATABASE_URL"] = f"sqlite:///./{cls.database_path.as_posix()}"
        os.environ["APP_JWT_SECRET_KEY"] = "test-secret-key"
        os.environ["APP_API_REQUEST_LOGGING_ENABLED"] = "false"

        from app.core.config import get_settings
        from app.core.security import create_access_token, hash_password
        from app.db.base import Base
        from app.db.session import get_session_factory, reset_db_state
        from app.entities.user import User
        import app.entities  # noqa: F401

        get_settings.cache_clear()
        reset_db_state()
        engine = create_engine(os.environ["APP_DATABASE_URL"], connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=engine)
        engine.dispose()

        session = get_session_factory()()
        try:
            seed_user = User(
                name="Seed",
                surname="User",
                email="seed@example.com",
                password_hash=hash_password("seedpassword"),
                is_active=True,
            )
            session.add(seed_user)
            session.commit()
            session.refresh(seed_user)
            cls.seed_token = create_access_token(str(seed_user.id))
        finally:
            session.close()

        from fastapi.testclient import TestClient
        from app.main import create_app

        cls.client = TestClient(create_app())

    @classmethod
    def tearDownClass(cls) -> None:
        from app.core.config import get_settings
        from app.db.session import reset_db_state

        cls.client.close()
        reset_db_state()
        get_settings.cache_clear()
        if cls.database_path.exists():
            for _ in range(5):
                try:
                    cls.database_path.unlink()
                    break
                except PermissionError:
                    time.sleep(0.1)
        os.environ.pop("APP_DATABASE_URL", None)
        os.environ.pop("APP_JWT_SECRET_KEY", None)
        os.environ.pop("APP_API_REQUEST_LOGGING_ENABLED", None)

    def test_health_check(self) -> None:
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 401)

    def test_login_and_protected_user_crud(self) -> None:
        unauthorized_response = self.client.get("/users")
        self.assertEqual(unauthorized_response.status_code, 401)

        register_response = self.client.post(
            "/register",
            json={
                "name": "Ada",
                "surname": "Lovelace",
                "email": "ada@example.com",
                "password": "supersecure",
                "is_active": True,
            },
        )
        self.assertEqual(register_response.status_code, 201)
        self.assertEqual(register_response.json()["email"], "ada@example.com")

        duplicate_register_response = self.client.post(
            "/register",
            json={
                "name": "Ada",
                "surname": "Lovelace",
                "email": "ada@example.com",
                "password": "supersecure",
                "is_active": True,
            },
        )
        self.assertEqual(duplicate_register_response.status_code, 409)

        login_response = self.client.post(
            "/login",
            json={
                "email": "ada@example.com",
                "password": "supersecure",
            },
        )
        self.assertEqual(login_response.status_code, 200)
        token = login_response.json()["access_token"]
        auth_headers = {"Authorization": f"Bearer {token}"}

        invalid_login_response = self.client.post(
            "/login",
            json={
                "email": "ada@example.com",
                "password": "wrongpassword",
            },
        )
        self.assertEqual(invalid_login_response.status_code, 401)
        self.assertEqual(invalid_login_response.json()["detail"], "Invalid username or password")

        seed_headers = {"Authorization": f"Bearer {self.seed_token}"}
        seed_health_response = self.client.get("/health", headers=seed_headers)
        self.assertEqual(seed_health_response.status_code, 200)

        health_response = self.client.get("/health", headers=auth_headers)
        self.assertEqual(health_response.status_code, 200)
        self.assertEqual(health_response.json()["status"], "ok")

        users_response = self.client.get("/users", headers=auth_headers)
        self.assertEqual(users_response.status_code, 200)
        created_user = next(user for user in users_response.json() if user["email"] == "ada@example.com")
        self.assertEqual(created_user["email"], "ada@example.com")
        self.assertNotIn("password_hash", created_user)

        read_response = self.client.get(f"/users/{created_user['id']}", headers=auth_headers)
        self.assertEqual(read_response.status_code, 200)
        self.assertEqual(read_response.json()["name"], "Ada")

        update_response = self.client.put(
            f"/users/{created_user['id']}",
            json={"surname": "Byron", "password": "newpassword"},
            headers=auth_headers,
        )
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.json()["surname"], "Byron")

        delete_response = self.client.delete(f"/users/{created_user['id']}", headers=auth_headers)
        self.assertEqual(delete_response.status_code, 204)

        missing_response = self.client.get(f"/users/{created_user['id']}", headers=auth_headers)
        self.assertEqual(missing_response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
