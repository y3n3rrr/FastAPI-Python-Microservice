import os
import time
import unittest

from sqlalchemy import create_engine, text


class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._previous_env = {
            "APP_DATABASE_SCHEMA": os.environ.get("APP_DATABASE_SCHEMA"),
            "APP_JWT_SECRET_KEY": os.environ.get("APP_JWT_SECRET_KEY"),
            "APP_API_REQUEST_LOGGING_ENABLED": os.environ.get("APP_API_REQUEST_LOGGING_ENABLED"),
        }
        cls.test_schema = f"migros_store_test_{int(time.time())}"
        os.environ["APP_DATABASE_SCHEMA"] = cls.test_schema
        os.environ["APP_JWT_SECRET_KEY"] = "test-secret-key"
        os.environ["APP_API_REQUEST_LOGGING_ENABLED"] = "false"

        from app.core.config import get_settings
        from app.core.security import create_access_token, hash_password
        from app.db.session import get_session_factory, reset_db_state
        from app.entities.user import User
        from alembic import command
        from alembic.config import Config

        get_settings.cache_clear()
        reset_db_state()
        settings = get_settings()
        if settings.database_url.startswith("sqlite"):
            raise RuntimeError("Tests are configured to use PostgreSQL; set APP_DATABASE_URL to a PostgreSQL database.")

        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")

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

        settings = get_settings()
        if not settings.database_url.startswith("sqlite"):
            engine = create_engine(settings.database_url, pool_pre_ping=True)
            with engine.begin() as connection:
                connection.execute(text(f'DROP SCHEMA IF EXISTS "{cls.test_schema}" CASCADE'))
            engine.dispose()

        reset_db_state()
        get_settings.cache_clear()

        for key, value in cls._previous_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

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

    def test_catalog_crud_flow(self) -> None:
        unauthorized_response = self.client.get("/catalog/brands")
        self.assertEqual(unauthorized_response.status_code, 401)

        register_response = self.client.post(
            "/register",
            json={
                "name": "Catalog",
                "surname": "Tester",
                "email": "catalog-tester@example.com",
                "password": "supersecure",
                "is_active": True,
            },
        )
        self.assertEqual(register_response.status_code, 201)

        login_response = self.client.post(
            "/login",
            json={
                "email": "catalog-tester@example.com",
                "password": "supersecure",
            },
        )
        self.assertEqual(login_response.status_code, 200)
        token = login_response.json()["access_token"]
        auth_headers = {"Authorization": f"Bearer {token}"}

        brand_create = self.client.post(
            "/catalog/brands",
            json={
                "name": "Migros Test Brand",
                "slug": "migros-test-brand",
                "description": "Test brand description",
                "logo_url": "https://example.com/logo.png",
                "is_active": True,
            },
            headers=auth_headers,
        )
        self.assertEqual(brand_create.status_code, 201)
        brand_id = brand_create.json()["id"]

        category_create = self.client.post(
            "/catalog/categories",
            json={
                "parent_id": None,
                "name": "Beverages Test",
                "slug": "beverages-test",
                "description": "Test category",
                "is_active": True,
            },
            headers=auth_headers,
        )
        self.assertEqual(category_create.status_code, 201)
        category_id = category_create.json()["id"]

        product_create = self.client.post(
            "/catalog/products",
            json={
                "category_id": category_id,
                "brand_id": brand_id,
                "name": "Orange Juice Test 1L",
                "slug": "orange-juice-test-1l",
                "description": "Test product",
                "is_active": True,
            },
            headers=auth_headers,
        )
        self.assertEqual(product_create.status_code, 201)
        product_id = product_create.json()["id"]

        variant_create = self.client.post(
            "/catalog/variants",
            json={
                "product_id": product_id,
                "sku": "SKU-TEST-001",
                "barcode": "8690000000001",
                "name": "1L",
                "color": None,
                "size": "1L",
                "price": "39.90",
                "compare_at_price": "44.90",
                "currency": "TRY",
                "weight_kg": "1.050",
                "is_active": True,
            },
            headers=auth_headers,
        )
        self.assertEqual(variant_create.status_code, 201)
        variant_id = variant_create.json()["id"]

        image_create = self.client.post(
            "/catalog/images",
            json={
                "product_id": product_id,
                "image_url": "https://example.com/product-test.jpg",
                "alt_text": "Product test image",
                "sort_order": 0,
                "is_primary": True,
            },
            headers=auth_headers,
        )
        self.assertEqual(image_create.status_code, 201)
        image_id = image_create.json()["id"]

        inventory_create = self.client.post(
            "/catalog/inventory",
            json={
                "variant_id": variant_id,
                "quantity": 25,
                "reserved_quantity": 3,
                "reorder_level": 8,
            },
            headers=auth_headers,
        )
        self.assertEqual(inventory_create.status_code, 201)
        inventory_id = inventory_create.json()["id"]

        products_list = self.client.get("/catalog/products", headers=auth_headers)
        self.assertEqual(products_list.status_code, 200)
        self.assertTrue(any(product["id"] == product_id for product in products_list.json()))

        product_update = self.client.put(
            f"/catalog/products/{product_id}",
            json={"description": "Updated test product"},
            headers=auth_headers,
        )
        self.assertEqual(product_update.status_code, 200)
        self.assertEqual(product_update.json()["description"], "Updated test product")

        inventory_update = self.client.put(
            f"/catalog/inventory/{inventory_id}",
            json={"quantity": 40, "reserved_quantity": 5},
            headers=auth_headers,
        )
        self.assertEqual(inventory_update.status_code, 200)
        self.assertEqual(inventory_update.json()["quantity"], 40)

        delete_image = self.client.delete(f"/catalog/images/{image_id}", headers=auth_headers)
        self.assertEqual(delete_image.status_code, 204)

        delete_inventory = self.client.delete(f"/catalog/inventory/{inventory_id}", headers=auth_headers)
        self.assertEqual(delete_inventory.status_code, 204)

        delete_variant = self.client.delete(f"/catalog/variants/{variant_id}", headers=auth_headers)
        self.assertEqual(delete_variant.status_code, 204)

        delete_product = self.client.delete(f"/catalog/products/{product_id}", headers=auth_headers)
        self.assertEqual(delete_product.status_code, 204)

        delete_category = self.client.delete(f"/catalog/categories/{category_id}", headers=auth_headers)
        self.assertEqual(delete_category.status_code, 204)

        delete_brand = self.client.delete(f"/catalog/brands/{brand_id}", headers=auth_headers)
        self.assertEqual(delete_brand.status_code, 204)


if __name__ == "__main__":
    unittest.main()
