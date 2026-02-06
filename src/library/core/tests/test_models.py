
import pytest
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError
from core.models import Book, Loan
from django.contrib.auth.models import User


@pytest.mark.django_db
class TestBookModel:
    def test_book_creation(self):
        book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            isbn="9781234567890"
        )
        assert book.id is not None
        assert book.is_available is True

    def test_isbn_validation(self):
        with pytest.raises(ValidationError):
            Book.objects.create(
                title="Invalid",
                author="Invalid",
                isbn="abc"
            )


@pytest.mark.django_db
class TestLoanModel:
    @pytest.fixture
    def setup(self):
        self.user = User.objects.create_user(username="testuser", password="pass")
        self.book = Book.objects.create(
            title="Test", author="Test", isbn="9781234567890"
        )
        return self.user, self.book

    def test_borrow_success(self, setup):
        user, book = setup
        loan = Loan.objects.create(
            user=user,
            book=book,
            due_date=timezone.now() + timedelta(days=14)
        )
        assert loan.is_active is True
        assert book.is_available is False

    def test_double_borrow_fails(self, setup):
        user, book = setup
        Loan.objects.create(
            user=user,
            book=book,
            due_date=timezone.now() + timedelta(days=14)
        )
        with pytest.raises(Exception):  # IntegrityError or ValidationError
            Loan.objects.create(
                user=User.objects.create_user(username="other", password="pass"),
                book=book,
                due_date=timezone.now() + timedelta(days=14)
            )

    def test_return_success(self, setup):
        user, book = setup
        loan = Loan.objects.create(
            user=user,
            book=book,
            due_date=timezone.now() + timedelta(days=14)
        )
        loan.returned_at = timezone.now()
        loan.save()
        assert loan.is_active is False
        assert book.is_available is True