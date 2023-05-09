import json
import pytest

from fastapi.testclient import TestClient


class TestUsersAPI:
    user_base = {
        "email": "admin@victorciurana.com",
        "username": "sonja",
        "name": "Sonja",
        "phone_number": "+34622141813",
        "address": "C:// valldemossa 30 2a Spain, 07010",
    }
    data = {**user_base, "password": "victor"}
    expected_response = {**user_base, "id": 1, "is_active": True}
    endpoint = "/api/v1/users/"
    editable_data = {"name": "newname", "phone_number": "+34622141814", "address": "123 Main US"}

    def test_create_user(self, client: TestClient) -> None:
        response = client.post(self.endpoint, data=json.dumps(self.data))
        assert response.status_code == 200
        assert response.json() == self.expected_response

    def test_create_user_email_taken(self, db_user, client: TestClient) -> None:
        response = client.post(self.endpoint, data=json.dumps(self.data))
        assert response.status_code == 400
        assert response.json()["detail"] == "Email already registered"

    def test_create_user_username_taken(self, db_user, client: TestClient) -> None:
        data = {**self.data, "email": "another@email.com"}
        response = client.post(self.endpoint, data=json.dumps(data))
        assert response.status_code == 400
        assert response.json()["detail"] == "Username already registered"

    def test_read_user(self, db_user, token_header, client: TestClient) -> None:
        response = client.get(self.endpoint, headers=token_header)
        assert response.status_code == 200
        assert response.json() == self.expected_response

    def test_read_user_invalid_token(
        self, db_user, invalid_token_header, client: TestClient
    ) -> None:
        response = client.get(self.endpoint, headers=invalid_token_header)
        assert response.status_code == 401

    def test_read_user_no_user(self, token_header, client: TestClient) -> None:
        response = client.get(self.endpoint, headers=token_header)
        assert response.status_code == 404

    def test_update_user(self, db_user, token_header, client: TestClient) -> None:
        response = client.put(
            self.endpoint, headers=token_header, data=json.dumps(self.editable_data)
        )
        assert response.status_code == 200
        assert response.json() == {**self.expected_response, **self.editable_data}

    def test_update_user_invalid_phone_number(self, db_user, token_header, client: TestClient) -> None:
        with pytest.raises(ValueError):
            response = client.put(
                self.endpoint, headers=token_header, data=json.dumps({**self.editable_data, "phone_number": "+34333222111"})
            )
            assert response.status_code == 422
            assert "Invalid phone number" in response.json()["detail"][0]["msg"]

    def test_update_user_invalid_token(
        self, db_user, invalid_token_header, client: TestClient
    ) -> None:
        response = client.put(
            self.endpoint,
            headers=invalid_token_header,
            data=json.dumps(self.editable_data),
        )
        assert response.status_code == 401

    def test_update_user_no_user(self, token_header, client: TestClient) -> None:
        response = client.put(
            self.endpoint, headers=token_header, data=json.dumps(self.editable_data)
        )
        assert response.status_code == 404

    def test_delete_user(self, db_user, token_header, client: TestClient) -> None:
        response = client.delete(self.endpoint, headers=token_header)
        assert response.status_code == 200
        assert response.json() == {"ok": True}

    def test_delete_user_invalid_token(
        self, db_user, invalid_token_header, client: TestClient
    ) -> None:
        response = client.delete(self.endpoint, headers=invalid_token_header)
        assert response.status_code == 401

    def test_delete_user_no_user(self, token_header, client: TestClient) -> None:
        response = client.delete(self.endpoint, headers=token_header)
        assert response.status_code == 404
