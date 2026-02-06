
# Register your models here.
from django.contrib import admin
from .models import Book, Loan

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'isbn', 'is_available', 'created_at')
    search_fields = ('title', 'author', 'isbn')

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('id', 'book', 'user', 'borrowed_at', 'due_date', 'returned_at', 'is_active')
    #list_filter = ('is_active',)
    search_fields = ('book__title', 'user__username')
