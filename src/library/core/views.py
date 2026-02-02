from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated 
from rest_framework.generics import RetrieveAPIView
from django.contrib.auth.models import User
from .serializers import RegisterSerializer  
from .permissions import IsAdminOrReadOnly, IsBorrowerOrAdminForLoan
from core.models import Loan 
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

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