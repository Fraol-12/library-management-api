import pytest
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from core.models import Book, Loan


@pytest.fixture
def user_staff_book():
    """Shared fixture: regular user, staff user, and one test book."""
    user = User.objects.create_user(username="borrower", password="pass")
    staff = User.objects.create_user(username="staff", password="pass", is_staff=True)
    book = Book.objects.create(
        title="Shared Test Book",
        author="Test Author",
        isbn="9781234567890"
    )
    return user, staff, book


@pytest.mark.django_db
class TestBookModel:
    def test_book_creation(self):
        book = Book.objects.create(
            title="Clean Code",
            author="Robert C. Martin",
            isbn="9780132350884"
        )
        assert book.pk is not None
        assert book.is_available is True

    def test_invalid_isbn_rejected(self):
        with pytest.raises(DjangoValidationError):
            Book.objects.create(
                title="Invalid",
                author="Invalid",
                isbn="abc123"
            )


@pytest.mark.django_db
class TestLoanDomainRules:
    def test_borrow_success_and_availability_flip(self, user_staff_book):
        user, staff, book = user_staff_book
        loan = Loan.objects.create(
            user=user,
            book=book,
            due_date=timezone.now() + timedelta(days=14)
        )
        assert loan.is_active is True
        assert book.is_available is False

    def test_double_borrow_rejected_by_constraint(self, user_staff_book):
        user, staff, book = user_staff_book
        Loan.objects.create(
            user=user,
            book=book,
            due_date=timezone.now() + timedelta(days=14)
        )
        with pytest.raises(Exception):  # IntegrityError from DB constraint
            Loan.objects.create(
                user=User.objects.create_user(username="other", password="pass"),
                book=book,
                due_date=timezone.now() + timedelta(days=14)
            )

    def test_return_resets_availability(self, user_staff_book):
        user, staff, book = user_staff_book
        loan = Loan.objects.create(
            user=user,
            book=book,
            due_date=timezone.now() + timedelta(days=14)
        )
        loan.returned_at = timezone.now()
        loan.save()
        assert loan.is_active is False
        book.refresh_from_db()
        assert book.is_available is True


@pytest.mark.django_db
class TestLoanAPI:
    @pytest.fixture
    def client(self):
        return APIClient()

    @pytest.fixture
    def regular_user(self):
        user = User.objects.create_user("user", password="pass")
        client = APIClient()
        client.force_authenticate(user)
        return user, client

    @pytest.fixture
    def staff_user(self):
        user = User.objects.create_user("staff", password="pass", is_staff=True)
        client = APIClient()
        client.force_authenticate(user)
        return user, client

    @pytest.fixture
    def book(self):
        return Book.objects.create(title="Test", author="Test", isbn="9781234567890")

    def test_borrow_requires_auth(self, client, book):
        response = client.post("/api/loans/", {"book": book.id, "due_date": "2026-03-20"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_borrow_success(self, regular_user, book):
        user, client = regular_user
        response = client.post("/api/loans/", {"book": book.id, "due_date": "2026-03-20"})
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["is_active"] is True
        assert "id" in response.data

    def test_borrow_blocked_if_overdue(self, user_staff_book, regular_user):
        user, client = regular_user   # ← use the authenticated client!
        _, staff, book = user_staff_book
        overdue_book = Book.objects.create(title="Overdue", author="Old", isbn="9999999999999")
        overdue_loan = Loan(
            user=user,
            book=overdue_book,
            borrowed_at=timezone.now() - timedelta(days=2),
            due_date=timezone.now() - timedelta(days=1)
        )
        overdue_loan.save(force_insert=True)  # skip clean()
        
        response = client.post("/api/loans/", {"book": book.id, "due_date": "2026-03-20"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "overdue" in str(response.data).lower()

    def test_max_loans_limit(self, user_staff_book, regular_user):
        user, client = regular_user
        _, staff, book = user_staff_book
        # Create 5 active loans
        for i in range(5):
            other_book = Book.objects.create(
                title=f"Book {i}",
                author="Test",
                isbn=f"978000000000{i}"
            )
            Loan.objects.create(
                user=user,
                book=other_book,
                due_date=timezone.now() + timedelta(days=14)
            )
        response = client.post("/api/loans/", {"book": book.id, "due_date": "2026-03-20"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "maximum" in str(response.data).lower() or "5" in str(response.data)


@pytest.mark.django_db
class TestPermissions:
    @pytest.fixture
    def client(self):
        return APIClient()

    @pytest.fixture
    def regular_client(self):
        user = User.objects.create_user("regular", password="pass")
        client = APIClient()
        client.force_authenticate(user)
        return client

    @pytest.fixture
    def staff_client(self):
        user = User.objects.create_user("staff", password="pass", is_staff=True)
        client = APIClient()
        client.force_authenticate(user)
        return client

    def test_create_book_staff_only(self, regular_client, staff_client):
        data = {"title": "Test", "author": "Test", "isbn": "9781234567890"}
        response = regular_client.post("/api/books/", data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

        response = staff_client.post("/api/books/", data)
        assert response.status_code == status.HTTP_201_CREATED