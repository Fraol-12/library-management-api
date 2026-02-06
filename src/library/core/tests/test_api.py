import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from core.models import Book


@pytest.mark.django_db
class TestBookAPI:
    @pytest.fixture
    def client(self):
        return APIClient()

    @pytest.fixture
    def staff_user(self):
        user = User.objects.create_user("staff", password="pass", is_staff=True)
        return user

    @pytest.fixture
    def regular_user(self):
        user = User.objects.create_user("user", password="pass")
        return user

    def test_public_book_list(self, client):
        response = client.get("/api/books/")
        assert response.status_code == status.HTTP_200_OK

    def test_create_book_staff_only(self, client, staff_user, regular_user):
        client.force_authenticate(regular_user)
        response = client.post("/api/books/", {"title": "Test", "author": "Test", "isbn": "1234567890123"})
        assert response.status_code == status.HTTP_403_FORBIDDEN

        client.force_authenticate(staff_user)
        response = client.post("/api/books/", {"title": "Test", "author": "Test", "isbn": "1234567890123"})
        assert response.status_code == status.HTTP_201_CREATED