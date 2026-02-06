from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Book, Loan


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
        validators=[validate_password],
    )
    password2 = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )

    class Meta:
        model = User
        fields = ("username", "email", "password", "password2")
        extra_kwargs = {
            "email": {"required": True},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Passwords don't match."})

        if attrs["username"].lower() == "admin":
            raise serializers.ValidationError(
                {"username": "This username is reserved."}
            )

        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        user = User.objects.create_user(**validated_data)
        user.is_staff = False
        user.is_superuser = False
        user.save()
        return user


class BookSerializer(serializers.ModelSerializer):
    is_available = serializers.BooleanField(read_only=True)

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "author",
            "isbn",
            "description",
            "created_at",
            "updated_at",
            "is_available",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "is_available"]


class LoanCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new loan (borrow action)"""

    class Meta:
        model = Loan
        fields = ["book", "due_date"]
        extra_kwargs = {
            "book": {"write_only": True},
            "due_date": {"required": True},
        }

    def validate_book(self, value):
        """Custom validation: book must be available"""
        if not value.is_available:
            raise serializers.ValidationError(
                "This book is currently not available for borrowing."
            )
        return value


class LoanDetailSerializer(serializers.ModelSerializer):
    """Full serializer for reading loan details (nested book info)"""

    book = BookSerializer(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    user = serializers.StringRelatedField(
        read_only=True
    )  # or serializers.StringRelatedField() for username

    class Meta:
        model = Loan
        fields = [
            "id",
            "book",
            "user",
            "borrowed_at",
            "due_date",
            "returned_at",
            "is_active",
            "is_overdue",
        ]
        read_only_fields = [
            "id",
            "user",
            "borrowed_at",
            "returned_at",
            "is_active",
            "is_overdue",
        ]
