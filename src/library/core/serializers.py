from django.contrib.auth.models import User
from rest_framework import serializers
from django.core import exceptions
from django.contrib.auth.password_validation import validate_password 
from .models import Book


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only = True,
        required = True,
        style={'input_type': 'password'},
        validators=[validate_password]
    )
    
    password2 = serializers.CharField(
        write_only = True,
        required = True,
        style={'input_type': 'password'}
    )
   
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2')
        extra_kwargs = {
            'email': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "password don't match."})
        
        if attrs['username'].lower() == 'admin':
            raise serializers.ValidationError({'username': 'this username is reserved.'})
        return attrs 
    
    def create(self, validated_data):
        validated_data.pop("password2")
        user = User.objects.create_user(**validated_data)
        user.is_staff = False
        user.is_superuser = False
        user.save()
        return user
    
class BookSerilaizer(serializers.ModelSerializer):
    is_available = serializers.BooleanField(read_only=True)

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'isbn', 'description',
            'created_at', 'updated_at', 'is_available'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_available']