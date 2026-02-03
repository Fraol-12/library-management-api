from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated 
from rest_framework.generics import RetrieveAPIView
from django.contrib.auth.models import User
from .serializers import RegisterSerializer, BookSerilaizer 
from .permissions import IsAdminOrReadOnly, IsBorrowerOrAdminForLoan
from core.models import Loan 
from rest_framework import status, viewsets
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Book
from django.db.models import Exists, OuterRef, Q


class MeView(APIView):
    permission_classes = [IsAuthenticated]


    def get(self, request):
        user = request.user 
        data = {
            'id': user.id,
            'username': user.username,
            'email' : user.email,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'date_joined': user.date_joined.isoformat(),
        }
        return Response(data)
'''

class UserDetailView(RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer 
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'username' 

'''


class TestPermissionView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request):
        return Response({'message': 'This is read only test (allowed for everyone)'})    
    
    def post(self, request):
        return Response({'message': 'Write succeeded - you must be stuff'})
    

class TestLoanPermissionView(APIView):
    permission_classes = [IsAuthenticated, IsBorrowerOrAdminForLoan]
    queryset = Loan.objects.all()

    def get_object(self):
        # For demo — get first loan (in real code use pk from url)
        return Loan.objects.first()
    
    def get(self, request):
        obj = self.get_object()
        self.check_object_permissions(request, obj)
        return Response({'loan_user': obj.user.username})
    
    def post(self, request):
        obj = self.get_object()
        self.check_object_permissions(request, obj)
        return Response({'message:' 'You can modify this loan'})

class RegisterView(APIView):
    permission_classes = []
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user':{
                    'id': user.id,
                    'username': user.username,
                    'email':user.email,
                }

            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerilaizer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by availability using subquery (efficient)
        available_only = self.request.query_params.get("available", 'false').lower() == 'true'
        if available_only:
            # Subquery: exclude books that have an active loan
            has_active_loan = Loan.objects.filter(
                book=OuterRef('pk'),
                returned_at__isnull=True
            )
            queryset = queryset.filter(~Exists(has_active_loan))

        # Optional: basic search by title or author
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(author__icontains=search)
            )

        # Ordering (default + query param)
        ordering = self.request.query_params.get('ordering', 'title')
        if ordering in ['title', '-title', 'author', '-author', 'created_at', '-created_at']:
            queryset = queryset.order_by(ordering)

        return queryset  
            