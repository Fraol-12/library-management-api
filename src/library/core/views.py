from core.models import Book, Loan
from django.db import transaction
from django.db.models import Exists, OuterRef, Q
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .permissions import IsAdminOrReadOnly, IsBorrowerOrAdminForLoan
from .serializers import (BookSerializer, LoanCreateSerializer,
                          LoanDetailSerializer, RegisterSerializer)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
            "date_joined": user.date_joined.isoformat(),
        }
        return Response(data)


"""

class UserDetailView(RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer 
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'username' 

"""


class TestPermissionView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request):
        return Response({"message": "This is read only test (allowed for everyone)"})

    def post(self, request):
        return Response({"message": "Write succeeded - you must be stuff"})


class TestLoanPermissionView(APIView):
    permission_classes = [IsAuthenticated, IsBorrowerOrAdminForLoan]
    queryset = Loan.objects.all()

    def get_object(self):
        # For demo — get first loan (in real code use pk from url)
        return Loan.objects.first()

    def get(self, request):
        obj = self.get_object()
        self.check_object_permissions(request, obj)
        return Response({"loan_user": obj.user.username})

    def post(self, request):
        obj = self.get_object()
        self.check_object_permissions(request, obj)
        return Response({"message:" "You can modify this loan"})


class RegisterView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                    },
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by availability using subquery (efficient)
        available_only = (
            self.request.query_params.get("available", "false").lower() == "true"
        )
        if available_only:
            # Subquery: exclude books that have an active loan
            has_active_loan = Loan.objects.filter(
                book=OuterRef("pk"), returned_at__isnull=True
            )
            queryset = queryset.filter(~Exists(has_active_loan))

        # Optional: basic search by title or author
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(author__icontains=search)
            )

        # Ordering (default + query param)
        ordering = self.request.query_params.get("ordering", "title")
        if ordering in [
            "title",
            "-title",
            "author",
            "-author",
            "created_at",
            "-created_at",
        ]:
            queryset = queryset.order_by(ordering)

        return queryset


class LoanViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return LoanCreateSerializer
        return LoanDetailSerializer  # renamed to LoanDetailSerializer for clarity

    def get_queryset(self):
        if self.request.user.is_staff:
            return Loan.objects.all()
        return Loan.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Call perform_create to enforce max_loans & overdue rules
        self.perform_create(serializer)
        # Get the saved loan object
        loan = serializer.instance



        response_serializer = LoanDetailSerializer(loan, context={"request": request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @transaction.atomic
    def perform_create(self, serializer):
        user = self.request.user
        book = serializer.validated_data['book']
        due_date = serializer.validated_data['due_date']

        # Rule A: Block borrow if overdue loans exist
        overdue = Loan.objects.filter(
            user=user,
            returned_at__isnull=True,
            due_date__lt=timezone.now()
        ).exists()
        if overdue:
            raise DRFValidationError({
                "detail": "You have overdue loans. Return them first or contact staff."
            })

        # Rule B: Max active loans
        max_loans = 5
        active_count = Loan.objects.filter(user=user, returned_at__isnull=True).count()
        if active_count >= max_loans:
            raise DRFValidationError({
                "detail": f"You can borrow at most {max_loans} books at a time. Return some first."
            })

        # Existing rules
        if due_date <= timezone.now():
            raise DRFValidationError({"due_date": "Due date must be in the future."})

        if Loan.objects.filter(book=book, returned_at__isnull=True).exists():
            raise DRFValidationError({"book": "This book is already borrowed."})

        # Save loan
        serializer.save(user=user)


    @action(
        detail=True,
        methods=["patch"],
        permission_classes=[IsBorrowerOrAdminForLoan],
        url_path="return",
    )
    @transaction.atomic
    def return_book(self, request, pk=None):
        loan = self.get_object()

        if loan.returned_at is not None:
            raise DRFValidationError(
                {"detail": "This book is already returned."},
            )
        if not (request.user == loan.user or request.user.is_staff):
            raise DRFValidationError(
                {"detail": "You can only return your own books (or be staff)."},
            )
        loan.returned_at = timezone.now()
        loan.save()

        return Response(LoanDetailSerializer(loan).data)

    @action(detail=False, methods=["get"], url_path="my-active")
    def my_active(self, request):
        loans = Loan.objects.filter(user=request.user, returned_at__isnull=True)
        serializer = LoanDetailSerializer(loans, many=True)
        return Response(serializer.data)
